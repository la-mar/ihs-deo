# type: ignore

from __future__ import annotations
from typing import Dict, List, Union, Optional
from datetime import datetime, date
import logging


import pandas as pd
from sqlalchemy.sql import func

from app import db


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class TimestampMixin(object):
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


logger = logging.getLogger(__name__)


class DataFrameMixin(object):
    """Base class for sqlalchemy ORM tables containing mostly utility
    functions for accessing table properties and managing insert, update,
    and upsert operations.
    """

    @classproperty
    def s(self):
        return db.session

    @classmethod
    def as_df(cls):
        query = cls.s.query(cls)
        return pd.read_sql(query.statement, query.session.bind)

    @classmethod
    def primary_key_columns(cls) -> List:
        """Returns a list of sqlalchemy column objects for this table's primary keys.

        Returns:
            list -- [Column1, Column2, ...]
        """

        # return [v for k, v in cls.__table__.c.items() if v.primary_key]
        return list(cls.__table__.primary_key.columns)

    @classmethod
    def primary_key_names(cls) -> List[str]:
        """Returns the column names of this table's primary keys.

        Returns:
            list -- column names
        """

        return list(cls.__table__.primary_key.columns.keys())

    @classmethod
    def primary_key_values(
        cls, as_list: bool = False, as_dict: bool = False
    ) -> Union[pd.DataFrame, List, Dict]:
        query = cls.s.query(cls).with_entities(*cls.primary_key_columns())
        df = pd.read_sql(query.statement, query.session.bind)
        if as_list:
            return list(df.squeeze().values)
        elif as_dict:
            return df.to_dict("records")
        else:
            return df

    @classmethod
    def primary_keys_updated_since(
        cls, dt: datetime, as_list: bool = False, as_dict: bool = False
    ) -> Union[pd.DataFrame, List, Dict]:
        query = (
            cls.s.query(cls)
            .with_entities(*cls.primary_key_columns())
            .filter(cls.updated_at >= dt)
        )
        df = pd.read_sql(query.statement, query.session.bind)
        if as_list:
            return list(df.squeeze().values)
        elif as_dict:
            return df.to_dict("records")
        else:
            return df

    @classmethod
    def foreign_key_columns(cls) -> List:
        """Returns a list of sqlalchemy column objects for this table's foreign keys.

        Returns:
            list -- [Column1, Column2, ...]
        """

        return list(cls.__table__.foreign_keys)

    @classmethod
    def foreign_key_values(
        cls, as_list: bool = False, as_dict: bool = False
    ) -> Union[pd.DataFrame, List, Dict]:
        query = cls.s.query(cls).with_entities(*cls.foreign_key_columns())
        df = pd.read_sql(query.statement, query.session.bind)
        if as_list:
            return list(df.squeeze().values)
        elif as_dict:
            return df.to_dict("records")
        else:
            return df

    @classmethod
    def foreign_keys_updated_since(
        cls, dt: datetime, as_list: bool = False, as_dict: bool = False
    ) -> Union[pd.DataFrame, List, Dict]:
        query = (
            cls.s.query(cls)
            .with_entities(*cls.foreign_key_columns())
            .filter(cls.updated_at >= dt)
        )
        df = pd.read_sql(query.statement, query.session.bind)
        if as_list:
            return list(df.squeeze().values)
        elif as_dict:
            return df.to_dict("records")
        else:
            return df

    @classmethod
    def records_updated_since(cls, dt: datetime):
        query = cls.s.query(cls).filter(cls.updated_at > dt)
        return pd.read_sql(query.statement, query.session.bind)

    @classmethod
    def column_names(cls) -> List[str]:
        return list(cls.__table__.columns.keys())

    @classmethod
    def column_types(cls) -> Dict[str, type]:
        return {colname: col.type for colname, col in cls.__table__.c.items()}

    @classmethod
    def column_python_types(cls) -> Dict[str, type]:
        return {
            colname: col.type.python_type for colname, col in cls.__table__.c.items()
        }

    @classmethod
    def fetch_all(cls) -> List:
        return cls.s.query(cls).all()

    @classmethod
    def get_session_state(cls, count=True) -> Dict[str, int]:
        if cls.s is not None:
            if count:
                return {
                    "new": len(cls.s.new),
                    "updates": len(cls.s.dirty),
                    "deletes": len(cls.s.deleted),
                }
            else:
                return {
                    "new": cls.s.new,
                    "updates": cls.s.dirty,
                    "deletes": cls.s.deleted,
                }

    @classmethod
    def merge_records(cls, df: pd.DataFrame, print_rec: bool = False) -> None:
        """Convert dataframe rows to object instances and merge into session by
        primary key matching.

        Arguments:
            df {pd.DataFrame} -- A dataframe of object attributes.

        Keyword Arguments:
            print {bool} -- Optional: Print record when inserting.

        Returns:
            None
        """
        # Drop rows with NA in a primary key
        df = df.dropna(subset=cls.primary_key_names())
        logger.info(f"Records to be inserted: {len(df)}")
        merged_objects = []
        nrecords = len(df)
        nfailed = 0
        for i, row in enumerate(df.iterrows()):
            try:

                merged_objects.append(
                    cls.s.merge(cls(**row[1].where(~pd.isna(row[1]), None).to_dict()))
                )
                if print_rec == True:
                    logger.info(f"{cls.__tablename__}: loaded {i} of {nrecords}")

            except Exception as e:
                logger.error(
                    f"""Failed to merge record: --""" + "\n\n"
                    f"""Invalid record: {i-1}/{len(df)}""" + "\n"
                    f"""    {row[1]}""" + "\n"
                    f""" {e} """
                )
                nfailed += 1

        # Add merged objects to session
        cls.s.add_all(merged_objects)
        logger.info(
            f"Successfully loaded {nrecords-nfailed} records to {cls.__tablename__}"
        )

    @classmethod
    def get_last_update(cls) -> datetime:
        """Get the datetime of the most recently updated record

        Returns:
            datetime
        """

        return cls.s.query(func.max(cls.__table__.c.updated_at)).first()

    @classmethod
    def nrows(cls) -> int:
        """Return a count of the number of rows in this table.

        Returns:
            int -- row count
        """

        return cls.s.query(
            func.count(cls.__table__.c[cls.primary_key_names()[0]])
        ).first()

    # @classmethod
    # def tz_convert(
    #     cls, ts: datetime, as_ts: bool = True, as_utc: bool = False
    # ) -> pd.Timestamp:

    #     if isinstance(ts, (datetime, date)):
    #         ts = pd.Timestamp(ts)

    #     has_tz = ts.tz is not None

    #     try:
    #         if has_tz:
    #             is_utc = ts.tz._utcoffset == 0
    #             if is_utc:
    #                 ts = ts.tz_convert("US/Central")
    #         else:
    #             ts = ts.tz_localize("US/Central")
    #     except Exception as e:
    #         logger.debug(f"Error normalizing timezone for value {ts}: {e}")

    #     if as_utc:
    #         ts = ts.tz_convert("utc")

    #     if not as_ts:
    #         ts = ts.to_pydatetime()

    #     return ts

    @classproperty
    def date_columns(cls):
        return [
            colname
            for colname, dtype in cls.column_python_types().items()
            if dtype in [datetime, date]
        ]

    def dtypes(cls) -> pd.DataFrame:
        result = {}
        for colname, col in cls.__table__.c.items():
            attrs = {}
            attrs["python_type"] = col.type.python_type
            try:
                attrs["sql_length"] = int(col.type.length)
            except:
                attrs["sql_length"] = 0
            attrs["sql_typename"] = col.type.__visit_name__
            attrs["type"] = col.type
            result[colname] = attrs
        result = pd.DataFrame.from_dict(result, orient="index")
        result.sql_length = result.sql_length.astype(int)
        return result

    @classmethod
    def persist(cls) -> None:
        """Propagate changes in session to database.

        Returns:
            None
        """
        try:
            # logger.info(cls.get_session_state())
            cls.s.flush()
            cls.s.commit()
        except Exception as e:
            # TODO: Sentry
            logger.info(e)
            cls.s.rollback()

    @classmethod
    def orm_load_updates(cls, updates: list) -> None:
        try:
            cls.s.add_all(updates)
            # Commit Updates
            cls.s.commit()
        except Exception as e:
            # TODO: Add Sentry
            cls.s.rollback()
            # cls.s.close()
            logger.info("Could not load updates")
            logger.info(e)

    @classmethod
    def orm_load_inserts(cls, inserts: pd.DataFrame) -> None:

        try:
            insert_records = []
            # To dict to pass to sqlalchemy
            for row in inserts.to_dict("records"):

                # Create record object and add to dml list
                insert_records.append(cls(**row))
            cls.s.add_all(insert_records)

            # Commit Insertions
            cls.s.commit()
        except Exception as e:
            # TODO: Add Sentry
            cls.s.rollback()
            # cls.s.close()
            logger.info("Could not load inserts")
            logger.info(e)

    @classmethod
    def bulk_insert(cls, df, size: int = 1000):
        df = df.where(pd.notnull(df), None)

        affected: int = 0
        for chunk in cls.chunks(df, size):
            records = cls.orient(cls.nan_to_none(df))

            cls.s.bulk_insert_mappings(cls, [i for i in records])
            cls.persist()
            logger.info(
                f"{cls.__table__.name}.bulk_insert: inserted {len(records)} records"
            )
            affected += len(records)
        return affected

    @classmethod
    def bulk_update(cls, df, size: int = 1000):
        df = df.where(pd.notnull(df), None)

        affected: int = 0
        for chunk in cls.chunks(df, size):

            records = cls.orient(cls.nan_to_none(df))

            cls.s.bulk_update_mappings(cls, [i for i in records])
            cls.persist()
            logger.info(
                f"{cls.__table__.name}.bulk_update: updated {len(records)} records"
            )
            affected += len(records)
        return affected

    @classmethod
    def bulk_merge(cls, df, core_insert=True):

        updates = cls.select_updates(df)
        inserts = cls.select_inserts(df)

        ins = 0
        ups = 0

        if not updates.empty:
            ups = cls.bulk_update(updates)

        if not inserts.empty:
            if core_insert:
                ins = cls.core_insert(inserts)
            else:
                ins = cls.bulk_insert(inserts)

        return {"updates": ups, "inserts": ins}

    @classmethod
    def bulk_save_objects(cls, objs: list):
        cls.s.bulk_save_objects(objs)

    @classmethod
    def _update_mask(cls, df: pd.DataFrame, as_series=False) -> list:
        """Breakdown keys to lists to get correct comparison"""

        dt_columns = df.select_dtypes(
            include=["datetime64[ns, UTC]", "datetime64[ns]"]
        ).columns.tolist()

        dfkeys = df[cls.primary_key_names()]
        tablekeys = cls.primary_key_values()

        pk_date_columns = [dt for dt in dt_columns if dt in dfkeys.columns]

        #! force datetime to date when part of primary key
        for column in pk_date_columns:
            dfkeys[column] = dfkeys[column].dt.date
            tablekeys[column] = tablekeys[column].dt.date

        dfkeys = dfkeys.to_records(index=False).tolist()
        tablekeys = tablekeys.to_records(index=False).tolist()
        mask = [x in tablekeys for x in dfkeys]
        if as_series:
            return pd.Series(mask)
        else:
            return mask

    @classmethod
    def _insert_mask(cls, df: pd.DataFrame, as_series=False) -> list:
        mask = ~cls._update_mask(df, as_series=True)
        if as_series:
            return mask
        else:
            return mask.values.tolist()

    @classmethod
    def select_updates(cls, df):
        updates = df[cls._update_mask(df)]

        dt_columns = updates.select_dtypes(
            include=["datetime64[ns, UTC]", "datetime64[ns]"]
        ).columns.tolist()

        dfkeys = updates[cls.primary_key_names()]

        pk_date_columns = [dt for dt in dt_columns if dt in dfkeys.columns]

        #! force datetime to date when part of primary key
        for column in pk_date_columns:
            updates[column] = updates[column].dt.date

        return updates

    @classmethod
    def select_inserts(cls, df):
        inserts = df[cls._insert_mask(df)]

        dt_columns = inserts.select_dtypes(
            include=["datetime64[ns, UTC]", "datetime64[ns]"]
        ).columns.tolist()

        dfkeys = inserts[cls.primary_key_names()]

        pk_date_columns = [dt for dt in dt_columns if dt in dfkeys.columns]

        #! force datetime to date when part of primary key
        for column in pk_date_columns:
            inserts[column] = inserts[column].dt.date

        return inserts

    @classmethod
    def core_insert(cls, df):
        records = cls.orient(cls.nan_to_none(df))

        cls.s.bind.engine.execute(cls.__table__.insert(), [i for i in records])
        cls.persist()
        logger.info(
            f"{cls.__table__.name}.core_insert: inserted {len(records)} records"
        )
        return len(records)

    @classmethod
    def nan_to_none(cls, df):
        return df.where(~pd.isna(df), None)

    @staticmethod
    def orient(df):
        return df.to_dict(orient="records")

    @staticmethod
    def chunks(df, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(df), n):
            yield df.loc[i : i + n - 1]

