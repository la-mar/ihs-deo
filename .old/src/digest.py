

from sqlalchemy import Column, MetaData, Table, create_engine, func
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.types import Integer, String, UserDefinedType
from sqlalchemy.event import listens_for
from datetime import datetime
from src.settings import DATABASE_URI,
import pandas as pd
import logging


logger = logging.getLogger(__name__)
# logging.getLogger('sqlalchemy.engine').setLevel(LOGLEVEL)
# logging.getLogger('sqlalchemy.orm').setLevel(LOGLEVEL)


class dbagent(object):

    def __init__(self, dbname, tables: list = None):

        self.engine = create_engine(DATABASE_URI+dbname)
        self.factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.factory)
        self.s = self.Session()
        self.meta = MetaData(bind = self.engine)
        # if tables:
        #     self.meta.reflect(only = tables, views = True)
        # else:
        #     self.meta.reflect(views = True)




driftwood = dbagent(DRIFTWOOD)
iwell = dbagent(IWELL)


@listens_for(Table, "column_reflect")
def column_reflect(inspector, table, column_info):
    # set column.key = "attr_<lower_case_name>"
    column_info['key'] = column_info['name'].lower()


Base = declarative_base()

class Geometry(UserDefinedType):

    def get_col_spec(self):
        return "GEOMETRY"

    # def __init__(self, srid = 4326):
    #     self.srid = srid

    # def bind_processor(self, dialect):
    #     def process(value):
    #         return value
    #     return process

    # def result_processor(self, dialect, coltype):
    #     def process(value):
    #         return value
    #     return process

    def bind_expression(self, bindvalue):
        return func.geo.STGeomFromText(bindvalue, 4326, type_=self)

    def column_expression(self, col):
        return func.geo.STAsText()  # (col, type_=self)

    # def python_type(self):
    #     return arcgis.geometry._types.Geometry

class STGeomFromText(GenericFunction):
    type = Geometry
    package = "geo"
    name = "GEOMETRY::STGeomFromText"
    identifier = "STGeomFromText"

class STAsText(GenericFunction):
    type = Geometry
    package = "geo"
    name = "GEOMETRY.STAsText"
    identifier = "STAsText"

class classproperty(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)

class GenericTable(object):

    __bind_key__ = None
    __table_args__ = None
    # __mapper_args__ = None
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
        return {colname: col.type for colname, col in
                cls.__table__.c.items()
                }

    @classmethod
    def ptypes(cls):
        return {colname: col.type.python_type for colname, col in
                cls.__table__.c.items()
                }

    @classproperty
    def types(cls) -> pd.DataFrame:
        result = {}
        for colname, col in cls.__table__.c.items():
            attrs = {}
            attrs['python_type'] = col.type.python_type
            try:
                attrs['sql_length'] = int(col.type.length)
            except:
                attrs['sql_length'] = 0
            attrs['sql_typename'] = col.type.__visit_name__
            attrs['type'] = col.type
            result[colname] = attrs
        result = pd.DataFrame.from_dict(result, orient = 'index')
        result.sql_length = result.sql_length.astype(int)
        return result

    @classmethod
    def get_existing_records(cls):
        return cls.session.query(cls).all()

    @classproperty
    def df(cls):
        query = cls.session.query(cls)
        return pd.read_sql(query.statement, query.session.bind)

    @classmethod
    def get_session_state(cls, count=True) -> dict:
        if cls.session is not None:
            if count:
                return {'new': len(cls.session.new),
                        'updates': len(cls.session.dirty),
                        'deletes': len(cls.session.deleted)
                        }
            else:
                return {'new': cls.session.new,
                        'updates': cls.session.dirty,
                        'deletes': cls.session.deleted
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
        df = df.dropna(subset=cls.get_pks())
        logger.info(f'Records to be inserted: {len(df)}')
        merged_objects = []
        nrecords = len(df)
        nfailed = 0
        for i, row in enumerate(df.iterrows()):
            try:

                merged_objects.append(cls.session.merge(
                    cls(**row[1].where(~pd.isna(row[1]), None).to_dict())))
                if print_rec == True:
                    logger.info(f'{cls.__tablename__}: loaded {i} of {nrecords}')

            except Exception as e:
                logger.error(
                    f'''Failed to merge record {e} --''' + '\n'
                    f'''({i-1}/{len(df)}): {row[1].where(~pd.isna(row[1]), None).to_dict()}''' + '\n'

                )
                nfailed += 1

        # Add merged objects to session
        cls.session.add_all(merged_objects)
        logger.info(
            f'Successfully loaded {nrecords-nfailed} records to {cls.__tablename__}')

    @classmethod
    def get_last_update(cls):
        return cls.session.query(func.max(cls.__table__.c.updated)).first()[0]

    @classmethod
    def records_updated_since(cls, dt: datetime = None):
        dt = dt or datetime.strptime('1970', '%Y')
        query = cls.session.query(cls).filter(cls.updated > dt)
        return pd.read_sql(query.statement, query.session.bind)

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
            logger.info('Could not load updates')
            logger.info(e)

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
            logger.info('Could not load inserts')
            logger.info(e)

    @classmethod
    def persist(cls) -> None:
        """Propagate changes in session to database.

        Returns:
            None
        """
        try:
            logger.info(cls.get_session_state())
            cls.session.commit()
        except Exception as e:
            #TODO: Sentry
            logger.info(e)
            cls.session.rollback()

class Flowback(GenericTable, Base):
    """ Driftwood.dbo.flowback"""
    __table_args__ = {'autoload': True,
                      'autoload_with': driftwood.engine,
                      'schema': 'dbo'
                      }
    __tablename__ = 'flowback'
    s = driftwood.Session()
    id = Column('id', Integer, primary_key = True)
    api14 = Column('api14')



'boph', 'gas', 'bwph',

class Production(GenericTable, Base):
    """ iWell.dbo.DEO_PRODUCTION_DAILY"""
    __table_args__ = {'autoload': True,
                      'autoload_with': iwell.engine,
                      'schema': 'dbo',
                      }

    __tablename__ = 'DEO_PRODUCTION_DAILY'
    s = iwell.Session()
    id = Column('production_id', Integer, primary_key = True)





if __name__ == "__main__":
    pass

    print(Production.cnames())
    print(Flowback.cnames())





