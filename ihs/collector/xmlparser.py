from __future__ import annotations
from typing import Callable, Dict, List, Union  # pylint: disable=unused-import
from collections import OrderedDict
import logging

import xmltodict
import util

from collector.parser import Parser

sp = util.StringProcessor()

logger = logging.getLogger(__name__)


class XMLParser(object):
    """ Transform an XML response into a normalized Python object"""

    def __init__(
        self,
        aliases: Dict[str, str] = None,
        exclude: List[str] = None,
        normalize: bool = False,
        parsers: List[Parser] = None,
    ):
        self.normalize = normalize
        self.aliases = aliases or {}
        self.exclude = exclude or []
        self.parsers = parsers or []
        self.errors: List[str] = []

    def __repr__(self):
        s = "s" if len(self.parsers) > 1 else ""
        return f"XMLParser: {len(self.parsers)} attached parser{s}"

    def add_parser(
        self, parser: Parser = None, ruleset: Dict[str, List] = None, name: str = None
    ):
        self.parsers.append(parser or Parser.init(ruleset, name=name))
        return self

    def normalize_keys(self, data: OrderedDict) -> OrderedDict:
        return util.apply_transformation(data, sp.normalize, keys=True, values=False)

    def parse_value_dtypes(self, data: OrderedDict) -> OrderedDict:
        for parser in self.parsers:
            data = util.apply_transformation(
                data, parser.parse, keys=False, values=True
            )
        return data

    def parse(self, xml: str, parse_dtypes: bool = True, **kwargs) -> OrderedDict:
        parsed = self.xml_to_dict(xml, **kwargs)
        parsed = self.normalize_keys(parsed)
        if parse_dtypes:
            parsed = self.parse_value_dtypes(parsed)
        return parsed

    def xml_to_dict(self, xml: str, **kwargs) -> OrderedDict:
        return xmltodict.parse(xml, **kwargs)

    @staticmethod
    def load_from_config(parser_conf: dict):
        parser_conf = parser_conf.get("parsers", parser_conf)
        parsers: List[Parser] = []
        for name, parser_def in parser_conf.items():
            ruleset = parser_def.get("rules", parser_def)
            parsers.append(Parser.init(ruleset, name))

        return XMLParser(parsers=parsers)
