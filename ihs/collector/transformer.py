from __future__ import annotations
from typing import Dict, List, Callable, Union
import logging
import lxml
import lxml.objectify
import lxml.etree

import requests
import pandas as pd


logger = logging.getLogger(__name__)


class Transformer(object):
    """ Unpacks a response object's json into a Pandas Dataframe"""

    date_handler_args: Dict[str, Union[str, int, bool]] = {
        "infer_datetime_format": True,
        "unit": "s",
        "errors": "coerce",
        "dayfirst": False,
        "yearfirst": False,
    }

    def __init__(
        self,
        aliases: Dict[str, str] = None,
        exclude: List[str] = None,
        normalize: bool = False,
        date_columns: List[str] = None,
        date_handler_args: Dict[str, Union[str, int, bool]] = None,
    ):
        self.normalize = normalize
        self.aliases = aliases or {}
        self.exclude = exclude or []
        self.date_columns = date_columns or []
        self.date_handler_args = date_handler_args or self.date_handler_args
        self.errors: List[str] = []

    def __repr__(self):
        return (
            f"Transformer: {len(self.aliases)} aliases, {len(self.exclude)} exclusions"
        )

    def transform(self, data: dict) -> pd.DataFrame:
        df = pd.DataFrame.from_records(data)
        df = self.apply_aliases(df)
        df = self.drop_exclusions(df)
        df = self.standardize_dates(df)
        if len(self.errors) > 0:
            logger.warning(
                f"Captured {len(self.errors)} parsing errors during transformation: {self.errors}"
            )
        return df

    def column_map(self, df: pd.DataFrame) -> Dict[str, str]:
        return {k: k for k in df.columns.tolist()}

    def apply_aliases(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=self.aliases)

    def drop_exclusions(self, df: pd.DataFrame):
        try:
            if len(self.exclude) > 0:
                logger.debug(f"Dropping {len(self.exclude)} columns: {self.exclude}")
            df = df.drop(columns=self.exclude)
        except Exception as e:
            msg = f"Failed attempting to drop columns -- {e}"
            self.errors.append(msg)
            logger.debug(msg)
        return df

    def safe_apply(
        self, df: pd.DataFrame, apply_to: str, func: Callable, apply_from: str = None
    ) -> pd.DataFrame:
        try:
            apply_from = apply_from or apply_to
            df[apply_to] = df[apply_from].apply(func)
        except KeyError:
            raise
        except Exception as e:
            msg = f"Unable to apply function to DataFrame: {e}"
            self.errors.append(msg)
            logger.debug(msg)
        return df

    def date_handler(self, value: str) -> Union[pd.Timestamp, pd.NaT]:
        try:
            dt = pd.to_datetime(value, **self.date_handler_args)
            if pd.isnull(dt):
                # TODO: Convert this into a default array of args at the class level
                modified_args = {**self.date_handler_args}
                modified_args.pop("unit", None)
                dt = pd.to_datetime(value, **modified_args)
            return dt
        except Exception as e:
            msg = f"Unable to convert value to datetime: {value} -- {e}"
            self.errors.append(msg)
            logger.debug(msg)
            return None

    def standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        for column_name in self.date_columns:
            try:
                df[column_name] = self.safe_apply(df, column_name, self.date_handler)[
                    column_name
                ]
            except KeyError as ke:
                msg = f"DataFrame has no date column named '{ke.args[0]}' -- {ke}"
                # self.errors.append(msg)
                logger.debug(msg)

        return df

    # def as_json(self):
    #     return [xmltodict.parse(xml) for xml in self.as_elements()]


if __name__ == "__main__":

    from collector.endpoint import load_from_config
    from config import get_active_config
    from collector.util import load_xml

    conf = get_active_config()
    endpoints = load_from_config(conf)
    endpoint = endpoints.get("wells")

    t = Transformer(
        aliases=endpoint.mappings.get("aliases"),
        exclude=endpoint.exclude,
        date_columns=["latest_production_time", "iwell_created_at", "iwell_updated_at"],
    )

    xml = load_xml("test/data/well_header_short.xml")

    def to_elements(xml: str):
        """Parse raw XML string into a python object

            Examples:
                Well: The results of a well query will be reduced to element trees
                        beginning at a WELLBORE element, then returned as an xml string.

                Production: The results of a well query will be reduced to element
                            trees beginning at a PRODUCING_ENTITY element, then
                            returned as an xml string.

            Returns:
                str - a string of xml
        """
        xml = lxml.objectify.fromstring(xml)
        root = xml.getroottree().getroot()
        xml = [child for child in root.getchildren() if child.tag == self.tag]
        return xml

    parsed = xmltodict.parse(xml)
    wellset = parsed.get("WELL_SET")
    wellset.keys()

    # lxml.etree.tostring(x)
