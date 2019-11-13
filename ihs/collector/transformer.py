from __future__ import annotations

import logging
from typing import Callable, Dict, List, Union  # pylint: disable=unused-import
from collections import OrderedDict

import xmltodict

import util
from collector.parser import Parser

sp = util.StringProcessor()

logger = logging.getLogger(__name__)


class Transformer(object):
    """ Transform an XML response into a normalized Python object"""

    def __init__(
        self,
        aliases: Dict[str, str] = None,
        exclude: List[str] = None,
        normalize: bool = False,
        date_columns: List[str] = None,
        parsers: List[Parser] = None,
    ):
        self.normalize = normalize
        self.aliases = aliases or {}
        self.exclude = exclude or []
        self.date_columns = date_columns or []
        self.parsers = parsers or []
        self.errors: List[str] = []

    def __repr__(self):
        return (
            f"Transformer: {len(self.aliases)} aliases, {len(self.exclude)} exclusions"
        )

    def add_parser(
        self, parser: Parser = None, ruleset: Dict[str, List] = None, name: str = None
    ):
        self.parsers.append(parser or Parser.init(ruleset, name=name))
        return self

    def normalize_keys(self, data: dict) -> dict:
        return util.apply_transformation(data, sp.normalize, keys=True, values=False)

    def parse_value_dtypes(self, data: dict) -> dict:
        for parser in self.parsers:
            data = util.apply_transformation(
                data, parser.parse, keys=False, values=True
            )
        return data

    def transform(self, xml: str, **kwargs) -> dict:
        parsed = self.xml_to_dict(xml)
        parsed = self.normalize_keys(parsed)
        return parsed

    def xml_to_dict(self, xml: str, **kwargs):
        return xmltodict.parse(xml, **kwargs)

    def handle_date(self, value: str):
        try:
            pass
        except Exception as e:
            msg = f"Unable to convert value to datetime: {value} -- {e}"
            self.errors.append(msg)
            logger.debug(msg)
            return None


class WellboreTransformer(Transformer):
    def transform(self, xml: str, **kwargs):
        parsed = super().transform(xml, **kwargs)

    # def extract_collections(self, data: OrderedDict) -> OrderedDict:
    #     """ Breakout root document into sub-documents """
    #     pass

    # def apply_metadata_to_collection(self, collection: OrderedDict) -> dict:
    #     pass

    def extract_metadata(self, root_document: OrderedDict) -> OrderedDict:
        return root_document.get("metadata", {})

    def extract_last_updated_date(self, root_document: OrderedDict) -> OrderedDict:
        return (
            root_document.get("header", {})
            .get("dates", {})
            .get({"last_update"}, {})
            .get("standard")
        )

    def copy_api_to_root(self, root_document: OrderedDict) -> OrderedDict:
        """ Moves a well's identification number (api) to the top level of
            the dictionary."""

        _id = root_document.get("metadata", {}).get("identification")
        if str(_id).isnumeric():
            if len(_id) == 14:
                root_document["api14"] = _id
                root_document["api10"] = _id[:10]
            elif len(_id) == 10:
                root_document["api10"] = _id

        root_document.move_to_end("api14", last=False)
        root_document.move_to_end("api10", last=False)

        return root_document


if __name__ == "__main__":

    from collector.endpoint import load_from_config
    from config import get_active_config

    logging.basicConfig()
    logger.setLevel(10)

    conf = get_active_config()
    endpoints = load_from_config(conf)
    endpoint = endpoints.get("wells")

    t = Transformer(aliases=endpoint.mappings.get("aliases"), exclude=endpoint.exclude)

    t.add_parser(
        ruleset=conf.PARSER_CONFIG["parsers"]["default"]["rules"], name="default"
    )

    xml = util.load_xml("test/data/well_header_short.xml")

    parsed = t.xml_to_dict(xml)
    parsed = t.normalize_keys(parsed)
    parsed = t.parse_value_dtypes(parsed)

    wellset = parsed.get("well_set")
    wellbore = wellset.get("wellbore")[0]
    len(wellbore)

    treatment_summary = wellbore.get("treatment_summary")
    print(treatment_summary)

    # util.to_json(wellbore[0], "example.json", cls=util.DateTimeEncoder)

