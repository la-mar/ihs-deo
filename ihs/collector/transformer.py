from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
import functools
from typing import Callable, Dict, List, Union  # pylint: disable=unused-import

from util import query_dict, ensure_list
from config import get_active_config

logger = logging.getLogger(__name__)
from util.geo import CoordinateTransformer

conf = get_active_config()

projector = CoordinateTransformer(conf.DEFAULT_PROJECTION)


class Transformer:

    collection_key: Union[str, None] = None
    entity_key: Union[str, None] = None

    @classmethod
    def add_document_hash(cls, data: OrderedDict) -> OrderedDict:
        data = cls.remove_variants(data)
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
        return query_dict("header.dates.last_update.standard", data or {})

    @classmethod
    def copy_last_update_to_root(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        data["ihs_last_update_date"] = cls.extract_last_updated_date(data)
        data.move_to_end("ihs_last_update_date", last=False)

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
    def remove_variants(cls, data: OrderedDict) -> OrderedDict:
        """ Remove fields that affect the output hash and are not representative of
            actual document changes """
        keys = ["date_creation"]
        for key in keys:
            data.pop(key, None)

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

    @classmethod
    def copy_content_to_root(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        get = functools.partial(query_dict, data=data.get("content", {}))

        data["ip_test_count"] = get("tests.initial_production")
        data["completion_count"] = get("engineering.completion")
        data["perforation_count"] = get("engineering.perforation")
        data["survey_count"] = get("surveys.borehole")
        return data

    @classmethod
    def project_well_locations(cls, data: OrderedDict) -> OrderedDict:
        """ Assemble and return the available well locations, usually SHL, PBHL, and ABHL """
        locs = {}
        loc_type_map = {
            "shl": ["surface", "shl"],
            "bhl": ["actual bottom hole", "abhl"],
            "pbhl": ["proposed bottom hole", "pbhl"],
        }

        location = data.get("location", [])

        if not issubclass(type(location), list):
            location = [location]

        for loc in location:
            get = functools.partial(query_dict, data=loc)
            type_name = loc.get("type_name", "").lower()
            type_code = loc.get("type_code", "").lower()
            datum = get("geographic.datum.code")

            for loc_name, loc_aliases in loc_type_map.items():
                if type_name in loc_aliases or type_code in loc_aliases:
                    lon, lat, crs = projector.transform(
                        x=get("geographic.longitude"),
                        y=get("geographic.latitude"),
                        crs=datum.lower() if datum else datum,
                    )
                    locs[loc_name] = {
                        "lon": lon,
                        "lat": lat,
                        "crs": crs,
                        "block": get("texas.block.number"),
                        "section": get("texas.section.number"),
                        "abstract": get("texas.abstract"),
                        "survey": get("texas.survey"),
                        "metes_bounds": get("texas.footage.concatenated"),
                    }
        data["location_wgs84"] = locs
        return data

    @classmethod
    def transform(cls, data: OrderedDict) -> OrderedDict:
        data = super().transform(data)
        data = cls.copy_content_to_root(data)
        data = cls.project_well_locations(data)
        return data


class ProductionTransformer(Transformer):

    collection_key = "production_set"
    entity_key = "producing_entity"

    @classmethod
    def extract_identifier(cls, data: OrderedDict) -> str:
        return str(query_dict("wellbore.metadata.identification", data))


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

    endpoint_name = "well_horizontal"
    task_name = "endpoint_check"
    job_config = [
        x for x in run_endpoint_task(endpoint_name, task_name) if x is not None
    ][0]

    job = submit_job(**job_config)
    xml = get_job_results(job)

    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    document = parser.parse(xml)
    transformed = WellboreTransformer.transform(document)

    # list(data.keys())
    # data["location_wgs84"]

    def get_active_survey(data: OrderedDict) -> OrderedDict:
        active_survey = OrderedDict()
        number = 0
        for s in ensure_list(data.get("surveys", {})):
            get = functools.partial(query_dict, data=s)
            n = get("borehole.header.number")
            if n > number:
                active_survey = get("borehole")
                number = n
        return active_survey

    #
    data = transformed[0]

    active_survey = get_active_survey(data)
    list(active_survey.keys())
    points = active_survey.get("point", [])

    get = functools.partial(query_dict, data=data)
    lon = get("location_wgs84.shl.lon")
    lat = get("location_wgs84.shl.lat")
    crs = get("location_wgs84.shl.crs")

    lat

    # TODO: start here
    # TODO: calculate survey points from x, y footages
    # TODO: use TOWGS84 to transform survey coordinates to wgs84

    # t["surveys"]["borehole"]

    # to_json(transformed, "test/data/production_sequoia.json")

    # collector = Collector(endpoints[job.endpoint].model)  # pylint: disable=no-member
    # collector.save(transformed)
