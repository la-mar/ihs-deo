from __future__ import annotations

import functools
import logging
from collections import OrderedDict
from typing import Dict, List, Union

import shapely.geometry as geometry
from flask_mongoengine import Document as Model

from config import get_active_config
from util import ensure_list, make_hash, query_dict
from util.geo import CoordinateTransformer, to_nad27sp, to_wgs84

logger = logging.getLogger(__name__)

conf = get_active_config()

projector = CoordinateTransformer(conf.DEFAULT_PROJECTION)


class Transformer:

    collection_key: Union[str, None] = None
    entity_key: Union[str, None] = None

    @classmethod
    def add_document_hash(cls, data: OrderedDict) -> OrderedDict:
        data = cls.remove_variants(data)
        hashes = {"document": make_hash(data)}
        data["hashes"] = hashes
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

            else:
                data["api14"] = None
                data["api10"] = None
            data.move_to_end("api10", last=False)
            data.move_to_end("api14", last=False)

        return data

    @classmethod
    def extract_identifier(cls, data: OrderedDict) -> str:
        return str(cls.extract_metadata(data).pop("identification", ""))

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
    def transform(cls, data: OrderedDict, model: Model) -> OrderedDict:
        data = data or OrderedDict()
        data = cls.copy_metadata_to_root(data)
        data = cls.copy_last_update_to_root(data)
        data = cls.copy_identifier_to_root(data)
        data = cls.add_document_hash(data)
        return data

    @classmethod
    def extract_from_collection(
        cls, document: OrderedDict, model: Model
    ) -> List[OrderedDict]:
        collection = document.get(cls.collection_key, document)
        data = collection.get(cls.entity_key, collection)
        if not isinstance(data, list):
            data = [data]

        transformed: List[OrderedDict] = []
        for record in data:
            transformed.append(cls.transform(record, model))

        logger.info(
            f"Extracted {len(transformed)} {cls.entity_key} from {cls.collection_key}"
        )
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
    def copy_operator_to_root(cls, data: OrderedDict) -> OrderedDict:
        data = data or OrderedDict()
        get = functools.partial(query_dict, data=data.get("header", {}))

        data["operator_name"] = get("operators.current.name")
        data["operator_alternate"] = get("operators.current.alternate")

        return data

    @classmethod
    def _project_well_locations(cls, data: OrderedDict) -> OrderedDict:
        """ Assemble and return the available well locations, usually SHL, PBHL, and ABHL """
        locs = OrderedDict()
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
                    result = {}
                    try:
                        lon, lat, crs = to_wgs84(
                            x=get("geographic.longitude"),
                            y=get("geographic.latitude"),
                            crs=datum.lower() if datum else datum,
                        )
                        # lon, lat, crs = projector.transform(
                        #     x=get("geographic.longitude"),
                        #     y=get("geographic.latitude"),
                        #     crs=datum.lower() if datum else datum,
                        # )
                        result["geom"] = geometry.mapping(geometry.Point(lon, lat))
                    except TypeError as te:
                        logger.debug(f"Failed transforming well location -- {te}")

                    result["block"] = get("texas.block.number")
                    result["section"] = get("texas.section.number")
                    result["abstract"] = get("texas.abstract")
                    result["survey"] = get("texas.survey")
                    result["metes_bounds"] = get("texas.footage.concatenated")

                    locs[loc_name] = result

        return locs

    @classmethod
    def create_geometries(cls, data: OrderedDict, existing: Model) -> OrderedDict:
        api14 = data.get("api14")
        locs = OrderedDict()  # type: ignore
        new_location_hash = data.get("hashes", {}).get("location")
        existing_location_hash = existing.hashes.get("location")
        if new_location_hash != existing_location_hash:
            logger.warning(f"{api14}: creating new locations")
            locs.update(cls._project_well_locations(data))
        else:
            logger.info(f"{api14}: location hashes match. Reusing existing locations.")
            locs["shl"] = existing.geoms.get("shl")
            locs["bhl"] = existing.geoms.get("bhl")
            locs["pbhl"] = existing.geoms.get("pbhl")

        if data.get("surveys") is not None:
            new_survey_hash = data.get("hashes", {}).get("survey")
            existing_survey_hash = existing.hashes.get("survey")
            if new_survey_hash != existing_survey_hash:
                logger.warning(f"{api14}: creating new survey")
                locs.update(cls._build_survey(data))
            else:
                if hasattr(existing, "geoms"):
                    logger.info(
                        f"{api14}: survey hashes match. Reusing existing surveys."
                    )
                    locs["survey_points"] = existing.geoms.get("survey_points")
                    locs["survey_line"] = existing.geoms.get("survey_line")

        data["geoms"] = locs
        return data

    @classmethod
    def get_active_survey(cls, data: OrderedDict) -> Union[OrderedDict, None]:
        """Return the most recent survey (survey with the highest 'number')"""
        active_survey = None
        number = 0
        for s in ensure_list(data.get("surveys", {})):
            get = functools.partial(query_dict, data=s)
            n = get("borehole.header.number") or -1
            if n > number:
                active_survey = get("borehole")
                number = n
        return active_survey

    @classmethod
    def _project_survey_points(
        cls, shlx: float, shly: float, points: List[Dict]
    ) -> List[Dict]:
        """ build a deviational survey based on the given parameters, projected to wgs84 """
        converted_points = []
        for idx, point in enumerate(points):
            get = functools.partial(query_dict, data=point)
            ns: Dict = get("north_south_coordinate") or {}
            ew: Dict = get("east_west_coordinate") or {}
            md: int = get("depths.measured.value")
            tvd: int = get("depths.true_vertical.value")
            dip: float = get("deviation.value")

            # XPATH
            ew_value = ew.get("value")
            new_x = None
            if ew_value and shlx:
                if ew.get("direction_code", "").lower() == "w":
                    new_x = shlx - float(ew_value)
                else:
                    new_x = shlx + float(ew_value)

            # YPATH
            ns_value = ns.get("value")
            new_y = None
            if ns_value and shly:
                if ns.get("direction_code", "").lower() == "s":
                    new_y = shly - float(ns_value)
                else:
                    new_y = shly + float(ns_value)

            if new_x and new_y:
                # TODO: incorporate dynamic datum/projection
                lon, lat, crs = to_wgs84(x=new_x, y=new_y, crs="nad27sp")

                converted_points.append(
                    {
                        "xy": (lon, lat),
                        "geom": geometry.mapping(geometry.Point(lon, lat)),
                        "md": md,
                        "tvd": tvd,
                        "dip": dip,
                    }
                )
                logger.debug(f"Transformed survey point {idx+1}/{len(points)}")

            else:
                logger.debug(
                    f"Failed transforming survey point: shlx={shlx}, shly={shly}, ew_value={ew_value}, ns_value={ns_value}, new_x={new_x}, new_y={new_y}"  # noqa
                )

        return converted_points

    @classmethod
    def _build_survey(cls, data: OrderedDict) -> OrderedDict:
        """ Return the well's survey and survey points projected to wgs84 """

        get = functools.partial(query_dict, data=data)
        active_survey = cls.get_active_survey(data)

        shllon = get("location.0.geographic.longitude")
        shllat = get("location.0.geographic.latitude")
        shlcrs = get("location.0.geographic.datum.code")

        x, y, new_crs = to_nad27sp(shllon, shllat, shlcrs)

        survey_points = []
        result = OrderedDict()
        if active_survey and len(active_survey.keys()) > 0:
            points = active_survey.get("point", None)

            if points and len(points) > 0:
                survey_points = cls._project_survey_points(x, y, points)
                result["survey_points"] = survey_points

            if survey_points and len(survey_points) > 0:
                try:
                    xys = [pt.pop("xy") for pt in survey_points]
                    result["survey_line"] = geometry.mapping(geometry.LineString(xys))

                except Exception as e:
                    logger.warning(f"Failed building survey line: {e.args[0]}")

        return result

    @classmethod
    def add_survey_hash(cls, data: OrderedDict) -> OrderedDict:
        data_for_hash = data.get("surveys")

        if data_for_hash is not None:
            data["hashes"]["survey"] = make_hash(data_for_hash)

        return data

    @classmethod
    def add_location_hash(cls, data: OrderedDict) -> OrderedDict:
        data_for_hash = data.get("location")

        if data_for_hash is not None:
            data["hashes"]["location"] = make_hash(data_for_hash)

        return data

    @classmethod
    def copy_header_to_root(cls, data: OrderedDict) -> OrderedDict:
        get = functools.partial(query_dict, data=data.get("header", {}))

        data["well_name"] = f'{get("designation.name")} {get("number")}'
        data["hole_direction"] = get("drilling.hole_direction.designation.code")
        data["status"] = get("statuses.current.name")
        return data

    @classmethod
    def transform(cls, data: OrderedDict, model: Model) -> OrderedDict:
        id = query_dict("metadata.identification", data=data)
        existing = model.objects(_id=str(id)).first() or model()
        if not hasattr(existing, "hashes"):
            existing.hashes = {}

        data = super().transform(data, model)
        data = cls.copy_header_to_root(data)
        data = cls.copy_content_to_root(data)
        data = cls.copy_operator_to_root(data)
        data = cls.add_survey_hash(data)
        data = cls.add_location_hash(data)
        data = cls.create_geometries(data, existing)
        return data


class ProductionTransformer(Transformer):

    collection_key = "production_set"
    entity_key = "producing_entity"

    @classmethod
    def add_production_hash(cls, data: OrderedDict) -> OrderedDict:
        data_for_hash = [data.get("wellbore"), data.get("production")]

        if data_for_hash is not None:
            data["hashes"]["production"] = make_hash(data_for_hash)

        return data

    @classmethod
    def extract_identifier(cls, data: OrderedDict) -> str:
        return str(query_dict("wellbore.metadata.identification", data))

    @classmethod
    def copy_header_to_root(cls, data: OrderedDict) -> OrderedDict:
        get = functools.partial(query_dict, data=data.get("header", {}))

        data["status"] = get("statuses.current.name")
        return data

    @classmethod
    def copy_identifier_to_root(cls, data: OrderedDict) -> OrderedDict:
        """ Moves a well's identification number (api) to the top level of
            the dictionary."""
        data = super().copy_identifier_to_root(data)
        _id = data.get("identification")
        if _id is not None:
            data["entity"] = _id
            data["entity12"] = _id[:12]
            data.move_to_end("entity", last=False)
            data.move_to_end("entity12", last=False)

        return data

    @classmethod
    def transform(cls, data: OrderedDict, model: Model) -> OrderedDict:

        data = super().transform(data, model)
        query_dict("metadata", data).pop("date_creation", None)
        query_dict("wellbore.metadata", data).pop("date_creation", None)
        data = cls.copy_header_to_root(data)
        data = cls.add_production_hash(data)

        return data


if __name__ == "__main__":

    from ihs import create_app

    from config import get_active_config
    from collector import XMLParser, Endpoint, Collector
    from collector.tasks import run_endpoint_task, get_job_results, submit_job, collect
    from util import to_json, load_json
    from time import sleep
    from api.models import WellHorizontal

    app = create_app()
    app.app_context().push()

    logging.basicConfig(level=20)

    conf = get_active_config()
    endpoints = Endpoint.from_yaml("tests/data/collector.yaml")
    task_name, endpoint_name, transformer = (
        "driftwood",
        "well_horizontal",
        WellboreTransformer,
    )
    # endpoint_name, transoformer = "production_horizontal", ProductionTransformer

    # endpoint_name = "production_vertical"
    # endpoint_name = "production_horizontal"
    # endpoint_name = "well_horizontal"
    # task_name = "endpoint_check"
    model = endpoints[endpoint_name].model
    job_config = [
        x for x in run_endpoint_task(endpoint_name, task_name) if x is not None
    ][0]

    job = submit_job(**job_config)
    sleep(3)
    xml = get_job_results(job)

    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    document = parser.parse(xml)

    # data = document["well_set"]["wellbore"][7]

    # data_collection = ProductionTransformer.extract_from_collection(document, model)
    data_collection = transformer.extract_from_collection(document, model)
    # data_collection[7]["api14"]
    # data = data_collection[0]
    # data_collection[0]["entity12"]
    # data_collection[0].keys()
    # document["production_set"]["producing_entity"]["hashes"]
    collector = Collector(endpoints[endpoint_name].model)
    collector.save(data_collection, replace=True)
    # obj = model.objects(api14="42461409160000").first()
    # [x["api14"] for x in results]

    # model.objects.update(unset__hashes__survey=1) # delete a key from all documents

    # for idx, obj in enumerate(model.objects):
    #     obj["hashes"]["survey"]

    # for idx, obj in enumerate(model.objects):
    #     try:
    #         data_for_hash = [obj.wellbore, obj.production]

    #         if data_for_hash is not None:
    #             obj["hashes"]["production"] = make_hash(data_for_hash)
    #         obj.save()
    #         print(f"updated {obj.api14} (count={idx})")

    #     except (KeyError, AttributeError):
    #         print(f"failed {obj.api14} (count={idx})")

    # missing_status = model.objects(entity12__exists=False)[0]
    # missing_status.id
