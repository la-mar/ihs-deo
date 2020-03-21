""" Mixin for MongoEngine backed well records """
import functools
import logging
from typing import Any, Dict, List, Union

from api.mixin import BaseMixin
from config import get_active_config
from util import gal_to_bbl, query_dict
from util.geo import CoordinateTransformer

logger = logging.getLogger(__name__)

conf = get_active_config()

projector = CoordinateTransformer(conf.DEFAULT_PROJECTION)


class WellMixin(BaseMixin):
    @property
    def well_header(self):
        """ Assemble and return the well's header information """

        output = {}

        if hasattr(self, "header"):
            data = self.header

        get = functools.partial(query_dict, data=data)

        output["api14"] = self.api14
        output["api10"] = self.api10
        output["last_update_at"] = self.last_update_at
        output["status"] = self.status

        output["well_name"] = get("designation.name")
        output["well_number"] = get("number")
        output["products"] = get("products.objective.code")
        output["hole_direction"] = get("drilling.hole_direction.designation.code")
        output["county_name"] = get("geopolitical.county.name")
        output["county_code"] = get("geopolitical.county.code")
        output["state_name"] = get("geopolitical.province_state.name")
        output["state_code"] = get("geopolitical.province_state.code")
        output["region_name"] = get("geopolitical.region.name")
        output["operator_name"] = get("operators.current.name")
        output["operator_alias"] = get("operators.current.alternate")

        return output

    @property
    def well_locations(self) -> Dict[str, Dict[str, Union[Any]]]:
        """ Assemble and return the available well locations, usually SHL, PBHL, and ABHL """
        geoms = {}
        # loc_type_map = {
        #     "shl": ["surface", "shl"],
        #     "bhl": ["actual bottom hole", "abhl"],
        #     "pbhl": ["proposed bottom hole", "pbhl"],
        # }

        # location = (
        #     self.location
        #     if issubclass(self.location.__class__, list)
        #     else [self.location]
        # )
        if hasattr(self, "geoms"):
            geoms = self.geoms
            # locs = {k: v for k, v in self.geoms.items() if k in ["shl", "bhl", "pbhl"]}
        # for loc in location:
        #     get = functools.partial(query_dict, data=loc)
        #     type_name = loc.get("type_name", "").lower()
        #     type_code = loc.get("type_code", "").lower()
        #     datum = get("geographic.datum.code")

        #     for loc_name, loc_aliases in loc_type_map.items():
        #         if type_name in loc_aliases or type_code in loc_aliases:
        #             lon, lat, crs = projector.transform(
        #                 x=get("geographic.longitude"),
        #                 y=get("geographic.latitude"),
        #                 crs=datum.lower() if datum else datum,
        #             )
        #             locs[loc_name] = {
        #                 "lon": lon,
        #                 "lat": lat,
        #                 "crs": crs,
        #                 "block": get("texas.block.number"),
        #                 "section": get("texas.section.number"),
        #                 "abstract": get("texas.abstract"),
        #                 "survey": get("texas.survey"),
        #                 "metes_bounds": get("texas.footage.concatenated"),
        #             }
        return geoms

    @property
    def active_survey(self) -> Dict[str, Any]:
        """ Return the currently active survey for the wellbore, projected to
            WGS84 (4326). The active survey is usually the most current survey
            that is reported for the wellbore. """

        shl_lat = query_dict("shl.lat", self.well_locations)
        shl_lon = query_dict("shl.lon", self.well_locations)

        data: Dict[str, dict] = {}
        header = {}
        points = []
        if hasattr(self, "surveys"):
            data = self["surveys"].get("borehole")

        get = functools.partial(query_dict, data=data)

        header["survey_type"] = get("type_code")
        header["survey_method"] = get("header.methods.survey.code")
        header["survey_end_date"] = get("header.dates.end.standard")
        header["survey_top"] = get("header.depths.top.value")
        header["survey_top_uom"] = get("header.depths.top.uom")
        header["survey_base"] = get("header.depths.base.value")
        header["survey_base_uom"] = get("header.depths.base.uom")

        # for point in get("point"):
        #     pt = {}
        #     pt["md"] = query_dict("depths.measured.value", point)
        #     pt["md_uom"] = query_dict("depths.measured.uom", point)
        #     pt["tvd"] = query_dict("depths.true_vertical.value", point)
        #     pt["tvd_uom"] = query_dict("depths.true_vertical.uom", point)
        #     pt["lon"] = shl_lon or 0 + query_dict("delta.longitude", point) or 0
        #     pt["lat"] = shl_lat or 0 + query_dict("delta.latitude", point) or 0
        #     points.append(pt)

        if hasattr(self, "geoms"):
            header["line"] = self.geoms.get("survey_line")
            header["points"] = self.geoms.get("survey_points")

        return header

    @property
    def ip_tests(self) -> List[Dict[str, Any]]:
        """ Assemble and return a list of initial production tests for the wellbore """
        data: Dict[str, dict] = {}
        output = []

        if hasattr(self, "tests"):
            data = self["tests"].get("ip_pt")

        if issubclass(data.__class__, dict):
            data = [data]  # type: ignore

        for test in data:
            try:
                get = functools.partial(query_dict, data=test)
                out = {}
                out["type_code"] = get("type_code")
                out["test_number"] = get("header.number")
                out["test_date"] = get("header.dates.test.standard")
                out["test_method"] = get("header.methods.test.name")
                out["completion"] = get("header.completion")
                out["oil"] = get("header.flows.oil.value")
                out["oil_uom"] = get("header.flows.oil.uom")
                out["gas"] = get("header.flows.gas.value")
                out["gas_uom"] = get("header.flows.gas.uom")
                out["water"] = get("header.flows.water.value")
                out["water_uom"] = get("header.flows.water.uom")
                choke = get("header.chokes.top.description")
                choke_uom = get("header.chokes.top.description")
                out["choke"] = f"{choke} {choke_uom}" if choke and choke_uom else None
                out["depth_top"] = get("header.depths.top.value")
                out["depth_top_uom"] = get("header.depths.top.uom")
                out["depth_base"] = get("header.depths.base.value")
                out["depth_base_uom"] = get("header.depths.base.uom")
                out["sulfur"] = get("header.sulfur.indicator.code")
                out["oil_gravity"] = get("header.gravities.oil.value")
                out["oil_gravity_uom"] = get("header.gravities.oil.uom")
                out["gor"] = get("header.ratios.gas_oil.value")
                out["gor_uom"] = get("header.ratios.gas_oil.uom")
                out["oil_gravity_uom"] = get("header.ratios.gas_oil.uom")
                try:
                    out["perf_upper"] = get("perforation.header.depths.top.value")
                    out["perf_upper_uom"] = get("perforation.header.depths.top.uom")
                    out["perf_lower"] = get("perforation.header.depths.base.value")
                    out["perf_lower_uom"] = get("perforation.header.depths.base.uom")
                    out["perfll"] = get(
                        "perforation.header.lengths.lateral_gross_perf.value"
                    )
                    out["perfll_uom"] = get(
                        "perforation.header.lengths.lateral_gross_perf.uom"
                    )
                except ValueError as ve:
                    logger.warning(f"{self.well_header['api14']} -- {ve}")
                    out["perf_upper"] = get("perforation.1.header.depths.top.value")
                    out["perf_upper_uom"] = get("perforation.1.header.depths.top.uom")
                    out["perf_lower"] = get("perforation.-1.header.depths.base.value")
                    out["perf_lower_uom"] = get("perforation.-1.header.depths.base.uom")
                    out["perfll"] = get(
                        "perforation.-1.header.lengths.lateral_gross_perf.value"
                    )
                    out["perfll_uom"] = get(
                        "perforation.-1.header.lengths.lateral_gross_perf.uom"
                    )

                output.append(out)
            except Exception as e:
                logger.error(f"{self.well_header['api14']} -- {e}")
        return output

    @property
    def frac(self) -> Dict[str, Union[int, float, str]]:
        """ Get the treatmen summary for the wellbore """
        data: Dict[str, dict] = {}
        output = {}

        if hasattr(self, "treatment_summary"):
            data = self["treatment_summary"]

        alias_map = {
            "gel_xlink": "xlink",
            "fluid_water": "water",
            "fluid_slick_water": "slick_water",
            "total_fluid": "fluid_total",
            "total_proppant": "proppant_total",
        }

        for key, item in data.items():
            if issubclass(item.__class__, dict):
                key_alias = alias_map.get(key, key)
                value, uom = gal_to_bbl(**item)
                output[key_alias] = value
                output[f"{key_alias}_uom"] = uom

        return output

    @property
    def well_elevations(self) -> Dict[str, Union[int, str]]:
        """ Get the reported ground and kelly bushing elevations for the well's
            surface location. """

        data: Dict[str, dict] = {}
        output = {}

        if hasattr(self, "header"):
            data = self["header"].get("elevations")

        get = functools.partial(query_dict, data=data)

        output["ground"] = get("ground.value")
        output["ground_uom"] = get("ground.uom")
        output["ground_code"] = get("ground.reference_code") or "GR"
        output["kb"] = get("kelly_bushing.value")
        output["kb_uom"] = get("kelly_bushing.uom")
        output["kb_code"] = get("kelly_bushing.code") or "KB"

        return output

    @property
    def well_dates(self) -> Dict[str, Union[int, str]]:
        """ Collection of relevant dates for the wellbore.

            Returns the following date fields, if available:
                - permit
                - permit_expiration
                - spud
                - comp
                - final_drill
                - rig_release
                - first_report
                - ihs_last_update

        """
        data: Dict[str, dict] = {}
        output = {}

        if hasattr(self, "header"):
            data = self["header"].get("dates")

        get = functools.partial(query_dict, data=data)

        output["permit"] = get("permit.standard")
        output["permit_expiration"] = get("permit_expiry.standard")
        output["spud"] = get("spud.standard")
        output["comp"] = get("completion.standard")
        output["final_drill"] = get("final_drilling.standard")
        output["rig_release"] = get("rig_release.standard")
        output["first_report"] = get("first_report.standard")
        output["ihs_last_update"] = get("last_update.standard")

        return output

    @property
    def well_statuses(self) -> Dict[str, str]:
        """ Current status names/codes assigned to the well"""
        data: Dict[str, dict] = {}
        output = {}

        if hasattr(self, "header"):
            data = self["header"].get("statuses")

        get = functools.partial(query_dict, data=data)

        output["current"] = get("current.name")
        output["current_code"] = get("current.code")
        output["activity"] = get("activity.name")
        output["activity_code"] = get("activity.code")

        return output
