from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
from typing import Callable, Dict, List, Union  # pylint: disable=unused-import

logger = logging.getLogger(__name__)


class Transformer:

    collection_key: Union[str, None] = None
    entity_key: Union[str, None] = None

    @classmethod
    def add_document_hash(cls, data: OrderedDict) -> OrderedDict:
        data["md5"] = hashlib.md5(str(data).encode()).hexdigest()
        data.move_to_end("md5", last=False)
        return data

    @classmethod
    def copy_identifier_to_root(cls, data: OrderedDict) -> OrderedDict:
        """ Moves a well's identification number (api) to the top level of
            the dictionary."""
        data = data or OrderedDict()

        _id = cls.extract_identifier(data)
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
    def extract_identifier(cls, data: OrderedDict) -> str:
        return str(cls.extract_metadata(data).get("identification", ""))

    @classmethod
    def extract_last_updated_date(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        return (
            data.get("header", {})
            .get("dates", {})
            .get("last_update", {})
            .get("standard")
        )

    @classmethod
    def copy_last_update_to_root(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        data["last_update"] = cls.extract_last_updated_date(data)
        data.move_to_end("last_update", last=False)

        return data

    @classmethod
    def extract_metadata(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        return data.get("metadata", {})

    @classmethod
    def copy_metadata_to_root(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        meta = cls.extract_metadata(data)
        for key, value in meta.items():
            data[key] = str(value)  # force to string
            data.move_to_end(key, last=False)

        return data

    @classmethod
    def transform(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        data = cls.copy_metadata_to_root(data)
        data = cls.copy_last_update_to_root(data)
        data = cls.copy_identifier_to_root(data)
        data = cls.add_document_hash(data)
        return data

    @classmethod
    def extract_from_collection(cls, document: OrderedDict) -> List[OrderedDict]:
        collection = document.get(cls.collection_key, document)
        data = collection.get(cls.entity_key, collection)
        if not isinstance(data, list):
            data = [data]

        transformed: List[OrderedDict] = []
        for record in data:
            transformed.append(cls.transform(record))

        logger.info(f"Extracted {len(transformed)} record from document")
        return transformed


class WellboreTransformer(Transformer):

    collection_key = "well_set"
    entity_key = "wellbore"


class ProductionTransformer(Transformer):

    collection_key = "production_set"
    entity_key = "producing_entity"

    @classmethod
    def extract_identifier(cls, data: OrderedDict) -> str:
        return str(
            data.get("wellbore", {}).get("metadata", {}).get("identification", "")
        )

    # @classmethod
    # def set_identifier_to_api(cls, data: OrderedDict) -> OrderedDict:
    #     data["producing_entity"] = data.get("identifier")
    #     data["identifier"] = cls.extract_identifier(data)
    #     return data


if __name__ == "__main__":

    from ihs import create_app

    from config import get_active_config
    from collector import XMLParser, Endpoint, Collector
    from collector.tasks import run_endpoint_task, get_job_results, submit_job, collect
    from util import to_json
    from time import sleep

    app = create_app()
    app.app_context().push()

    logging.basicConfig(level=20)

    conf = get_active_config()
    endpoints = Endpoint.load_from_config(conf)

    endpoint_name = "production_horizontal"
    task_name = "sequoia"
    job_config = [
        x for x in run_endpoint_task(endpoint_name, task_name) if x is not None
    ][0]

    job = submit_job(**job_config)
    xml = get_job_results(job)

    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    document = parser.parse(xml)
    transformed = ProductionTransformer.extract_from_collection(document)
    to_json(transformed, "test/data/production_parsed.json")

    # collector = Collector(endpoints[job.endpoint].model)  # pylint: disable=no-member
    # collector.save(transformed)
