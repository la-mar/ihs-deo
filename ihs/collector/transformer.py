from __future__ import annotations

import logging
from typing import Callable, Dict, List, Union  # pylint: disable=unused-import

import xmltodict

import util
from util.stringprocessor import StringProcessor

sp = StringProcessor()

logger = logging.getLogger(__name__)


class Transformer(object):
    """ Transform an XML response into a normalized Python object"""

    def __init__(
        self,
        aliases: Dict[str, str] = None,
        exclude: List[str] = None,
        normalize: bool = False,
        date_columns: List[str] = None,
    ):
        self.normalize = normalize
        self.aliases = aliases or {}
        self.exclude = exclude or []
        self.date_columns = date_columns or []
        self.errors: List[str] = []

    def __repr__(self):
        return (
            f"Transformer: {len(self.aliases)} aliases, {len(self.exclude)} exclusions"
        )

    def normalize_keys(self, data: dict) -> dict:
        return util.transform_keys(data, sp.normalize)

    def transform(self, xml: str, **kwargs) -> dict:
        parsed = self.parse_xml(xml)
        parsed = self.normalize_keys(parsed)
        return parsed

    def parse_xml(self, xml: str, **kwargs):
        return xmltodict.parse(xml, **kwargs)

    def handle_date(self, value: str):
        try:
            pass
        except Exception as e:
            msg = f"Unable to convert value to datetime: {value} -- {e}"
            self.errors.append(msg)
            logger.debug(msg)
            return None


if __name__ == "__main__":

    from collector.endpoint import load_from_config
    from config import get_active_config

    conf = get_active_config()
    endpoints = load_from_config(conf)
    endpoint = endpoints.get("wells")

    t = Transformer(aliases=endpoint.mappings.get("aliases"), exclude=endpoint.exclude,)

    xml = util.load_xml("test/data/well_header_short.xml")

    parsed = t.parse_xml(xml)
    parsed = t.normalize_keys(parsed)
    parsed.keys()

    wellset = parsed.get("well_set")
    wellbore = wellset.get("wellbore")
    len(wellbore)

    wellbore[0].get("treatment_summary")

    util.to_json(wellbore[0], "example.json")
