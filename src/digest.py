import pandas as pd
import shapely
import geopandas as gp
from pymssql import connect
from pandas import read_sql
from shapely.wkt import loads
from geopandas import GeoDataFrame
from math import radians, sin, cos, acos
import numpy as np

URI = 'mssql+pymssql://DWENRG-SQL01\\DRIFTWOOD_DB/'
DRIFTWOOD = 'Driftwood'
IHS = 'IHS'

CRS = {'init': 'epsg:4326'}


pd.options.display.max_rows = 1000
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('large_repr', 'truncate')
pd.set_option('precision',2)



def rd_sql(server, database, table, col_names=None, where_col=None, where_val=None, geo_col=False, epsg=4326, export=False, path='save.csv'):
    """
    Imports data from MSSQL database, returns GeoDataFrame. Specific columns can be selected and specific queries within columns can be selected. Requires the pymssql package, which must be separately installed.
    Arguments:
    server -- The server name (str). e.g.: 'SQL2012PROD03'
    database -- The specific database within the server (str). e.g.: 'LowFlows'
    table -- The specific table within the database (str). e.g.: 'LowFlowSiteRestrictionDaily'
    col_names -- The column names that should be retrieved (list). e.g.: ['SiteID', 'BandNo', 'RecordNo']
    where_col -- The sql statement related to a specific column for selection (must be formated according to the example). e.g.: 'SnapshotType'
    where_val -- The WHERE query values for the where_col (list). e.g. ['value1', 'value2']
    geo_col -- Is there a geometry column in the table?
    epsg -- The coordinate system (int)
    export -- Should the data be exported
    path -- The path and csv name for the export if 'export' is True (str)
    """
    if col_names is None and where_col is None:
        stmt1 = 'SELECT * FROM ' + table
    elif where_col is None:
        stmt1 = 'SELECT ' + str(col_names).replace('\'', '"')[1:-1] + ' FROM ' + table
    else:
        # stmt1 = 'SELECT ' + str(col_names).replace('\'', '"')[1:-1] + ' FROM ' + table + ' WHERE ' + str([where_col]).replace('\'', '"')[1:-1] + ' IN (' + str(where_val)[1:-1] + ')'
        stmt1 = 'SELECT ' + '*' + ' FROM ' + table + ' WHERE ' + where_col + " IN ('" + str(where_val) + "')"
    conn = connect(server, database=database)
    df = read_sql(stmt1, conn)

    ## Read in geometry if required
    if geo_col:
        geo_col_stmt = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=" + "\'" + table + "\'" + " AND DATA_TYPE='geometry'"
        geo_col = str(read_sql(geo_col_stmt, conn).iloc[0,0])
        if where_col is None:
            stmt2 = 'SELECT ' + geo_col + '.STGeometryN(1).ToString()' + ' FROM ' + table
        else:
            stmt2 = 'SELECT ' + geo_col + '.STGeometryN(1).ToString()' + ' FROM ' + table + ' WHERE ' + where_col + " IN ('" + str(where_val) + "')"
        df2 = read_sql(stmt2, conn)
        df2.columns = ['geometry']
        geometry = [loads(x) for x in df2.geometry]
        df = GeoDataFrame(df, geometry=geometry, crs={'init' :'epsg:' + str(epsg)})

    if export:
        df.to_csv(path, index=False)

    conn.close()
    return(df)


def distance(s_lat, s_lng, e_lat, e_lng):
    """returns distance between lat/longs in miles"""

    # approximate radius of earth in km
    R = 6373.0

    s_lat = s_lat*np.pi/180.0
    s_lng = np.deg2rad(s_lng)
    e_lat = np.deg2rad(e_lat)
    e_lng = np.deg2rad(e_lng)

    d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2

    # 2 * (radius of earth) *
    return 2 * R * np.arcsin(np.sqrt(d)) * 0.621371


apis = rd_sql('DWENRG-SQL01\\DRIFTWOOD_DB', 'Driftwood', 'MB_HORIZONTAL_SHL_ALL', geo_col = True, col_names = ['api', 'hole_direction', 'is_producing', 'Lat_SHL', 'Long_SHL', 'Shape'])

apis = apis.set_index('api').drop(columns = ['Shape'])
apis = apis[~apis.index.duplicated(keep='first')]


sequoia = apis.loc[['42461409160000']]
sequoia_geometry = sequoia.geometry[0]


apis['distance_to_sequoia'] = apis.geometry.apply(lambda geom: distance(geom.y, geom.x, sequoia_geometry.y, sequoia_geometry.x))


test = apis.iloc[0][['distance_to_sequoia']]



from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.util import object_state
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base, as_declarative, declared_attr, DeferredReflection
from sqlalchemy.event import listens_for
from sqlalchemy.sql import select
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.types import Integer, String, Float
from sqlalchemy.types import FLOAT, INTEGER, VARCHAR, DATE, DATETIME



_DEFAULT_EXCLUSIONS = ['updated', 'inserted']

SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://DWENRG-SQL01\\DRIFTWOOD_DB/'

engine = create_engine(SQLALCHEMY_DATABASE_URI+'Driftwood')
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base(bind=engine)


# kingdom_agent()


class GenericTable(object):

	__bind_key__ = None
	# __table__ = Table('WELLS', Base.metadata, autoload=True)
	__table_args__ = None
	__mapper_args__ = None
	__tablename__ = None

	session = None


	@classmethod
	def get_pks(cls):
		# Return list of primary key column names
		return cls.__table__.primary_key.columns.keys()

	@classmethod
	def get_pk_cols(cls):
		pk_cols = []
		for k, v in cls.__table__.c.items():
			if v.primary_key:
				pk_cols.append(v)
		return pk_cols


	@classmethod
	def get_ids(cls):
		return cls.session.query(cls).with_entities(*cls.get_pk_cols()).all()

	@classmethod
	def keys(cls):
		query = cls.session.query(cls).with_entities(*cls.get_pk_cols())
		return list(pd.read_sql(query.statement, query.session.bind).squeeze().values)

	@classmethod
	def keyedkeys(cls):
		# return self.df[[self.aliases['id']]].to_dict('records')
		query = cls.session.query(cls).with_entities(*cls.get_pk_cols())
		return pd.read_sql(query.statement, query.session.bind).to_dict('records')

	@classmethod
	def cnames(cls):
		return cls.__table__.columns.keys()

	@classmethod
	def ctypes(cls):
		return { colname : col.type for colname, col in
					cls.__table__.c.items()
					}

	@classmethod
	def ptypes(cls):
		return { colname : col.type.python_type for colname, col in
					cls.__table__.c.items()
					}


	@classmethod
	def get_inspector(cls):
		return inspect(cls.__table__)

	@classmethod
	def get_existing_records(cls):
		return cls.session.query(cls).all()

	# FIXME:
	# @classmethod
	# def get_existing_ids(cls):
	#         return cls.session.query(cls.__table__.columns.keys()).all()
	@classmethod
	def get_session_state(cls, count = True) -> dict:
		if cls.session is not None:
			if count:
				return {'new' : len(cls.session.new),
						'updates' : len(cls.session.dirty),
						'deletes' : len(cls.session.deleted)
						}
			else:
				return {'new' : cls.session.new,
						'updates' : cls.session.dirty,
						'deletes' : cls.session.deleted
						}

	@classmethod
	def merge_records(cls, df: pd.DataFrame, print_rec: bool = False) -> None:
		"""Convert dataframe rows to object instances and merge into session by
		primary key matching.

		Arguments:
			df {pd.DataFrame} -- A dataframe of object attributes

		Keyword Arguments:
			print {bool} -- Optional: Print record prior to insertion.

		Returns:
			None
		"""

		# Drop rows with NA in a primary key
		df = df.dropna(subset = cls.get_pks())
		print(f'Records to be inserted: {len(df)}')
		merged_objects = []
		ct = len(df)
		for i, row in enumerate(df.iterrows()):
			if print_rec == True:
				print(f'{cls.__tablename__}: loading {i} of {ct}')
			merged_objects.append(cls.session.merge(cls(**row[1].where(~pd.isna(row[1]), None).to_dict())))

		# Add merged objects to session
		cls.session.add_all(merged_objects)

	@classmethod
	def get_last_update(cls):
		return cls.session.query(func.max(cls.__table__.c.updated)).first()

	@classmethod
	def nrows(cls):
		return cls.session.query(func.count(cls.__table__.c[cls.get_pks()[0]])).first()

	@classmethod
	def load_updates(cls, updates: list) -> None:
		try:
			cls.session.add_all(updates)
			# Commit Updates
			cls.session.commit()
		except Exception as e:
			# TODO: Add Sentry
			cls.session.rollback()
			# cls.session.close()
			print('Could not load updates')
			print(e)

	@classmethod
	def load_inserts(cls, inserts: pd.DataFrame) -> None:

		try:
			insert_records = []
			# To dict to pass to sqlalchemy
			for row in inserts.to_dict('records'):

				# Create record object and add to dml list
				insert_records.append(cls(**row))
			cls.session.add_all(insert_records)

			# Commit Insertions
			cls.session.commit()
		except Exception as e:
			# TODO: Add Sentry
			cls.session.rollback()
			# cls.session.close()
			print('Could not load inserts')
			print(e)

	@classmethod
	def persist(cls) -> None:
		"""Propagate changes in session to database.

		Returns:
			None
		"""
		try:
			pprint(cls.get_session_state())
			cls.session.commit()
		except Exception as e:
			#TODO: Sentry
			print(e)
			cls.session.rollback()

class DriftwoodTable(GenericTable):
	#** Default Metadata args for Kingdom tables
	# __bind_key__ = 'Greater_Permian_Basin_1'
	__table_args__ = {'autoload': True}
	__tablename__ = None
	__mapper_args__ = {
					'exclude_properties' : _DEFAULT_EXCLUSIONS,
					}
	session = Session()


class Well_Header(DriftwoodTable, Base):
	__tablename__ = 'WELL_HEADER'


Well_Header.ctypes()


from pprint import pprint
test = test.to_frame().T.reset_index()
test = test.rename(columns = {'index' : 'API'})

Well_Header.merge_records(test)
Well_Header.persist()

# NOTE: WOrks!
