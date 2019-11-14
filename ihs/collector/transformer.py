from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
from typing import Callable, Dict, List, Union  # pylint: disable=unused-import


import util

logger = logging.getLogger(__name__)


class WellboreTransformer:
    @classmethod
    def extract_metadata(cls, data: OrderedDict) -> OrderedDict:
        return data.get("metadata", {})

    @classmethod
    def extract_last_updated_date(cls, data: OrderedDict) -> OrderedDict:
        return (
            data.get("header", {})
            .get("dates", {})
            .get("last_update", {})
            .get("standard")
        )

    @classmethod
    def copy_api_to_root(cls, data: OrderedDict) -> OrderedDict:
        """ Moves a well's identification number (api) to the top level of
            the dictionary."""

        _id = str(cls.extract_metadata(data).get("identification", ""))
        if _id.isnumeric():
            if len(_id) == 14:
                data["api14"] = _id
                data["api10"] = _id[:10]
            elif len(_id) == 10:
                data["api10"] = _id

        data.move_to_end("api10", last=False)
        data.move_to_end("api14", last=False)

        return data

    @classmethod
    def copy_metadata_to_root(cls, data: OrderedDict) -> OrderedDict:
        meta = cls.extract_metadata(data)
        for key, value in meta.items():
            data[key] = str(value)  # force to string
            data.move_to_end(key, last=False)

        return data

    @classmethod
    def copy_last_update_to_root(cls, data: OrderedDict) -> OrderedDict:
        data["last_update"] = cls.extract_last_updated_date(data)
        data.move_to_end("last_update", last=False)

        return data

    @classmethod
    def add_document_hash(cls, data: OrderedDict) -> OrderedDict:
        data["md5"] = hashlib.md5(str(data).encode()).hexdigest()
        data.move_to_end("md5", last=False)
        return data

    @classmethod
    def transform(cls, data: OrderedDict) -> OrderedDict:
        parsed = cls.copy_metadata_to_root(data)
        parsed = cls.copy_last_update_to_root(parsed)
        parsed = cls.copy_api_to_root(parsed)
        parsed = cls.add_document_hash(parsed)
        return parsed

    @classmethod
    def extract_from_wellset(cls, document: OrderedDict) -> List[OrderedDict]:
        wellset = document.get("well_set", document)
        wellbores = wellset.get("wellbore", wellset)

        transformed_wellbores: List[OrderedDict] = []
        for wb in wellbores:
            transformed_wellbores.append(WellboreTransformer.transform(wb))

        logger.info(f"Extracted {len(transformed_wellbores)} from document")
        return transformed_wellbores


if __name__ == "__main__":

    from collector.endpoint import load_from_config
    from config import get_active_config
    from collector.xmlparser import XMLParser

    logging.basicConfig()
    logger.setLevel(10)

    conf = get_active_config()
    endpoints = load_from_config(conf)
    endpoint = endpoints.get("wells")

    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)

    # parser.add_parser(
    #     ruleset=conf.PARSER_CONFIG["parsers"]["default"]["rules"], name="default"
    # )

    xml = util.load_xml("test/data/well_header_short.xml")

    document = parser.parse(xml)
    wellset = document.get("well_set", document)
    wellbores = wellset.get("wellbore", wellset)

    transformed_wellbores: List[OrderedDict] = []
    for wb in wellbores:
        transformed_wellbores.append(WellboreTransformer.transform(wb))

