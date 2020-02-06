""" Mixin for MongoEngine backed production records """

import functools
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Union

from api.mixin import BaseMixin
from config import get_active_config
from util import gal_to_bbl, query_dict
from util.geo import CoordinateTransformer

conf = get_active_config()


class ProductionMixin(BaseMixin):
    @property
    def statuses(self) -> Dict:
        output: Dict = OrderedDict()
        data: Dict = {}

        if hasattr(self, "header"):
            data = self.header.get("statuses")

        get = functools.partial(query_dict, data=data)

        output["current"] = get("current.name")
        output["current_code"] = get("current.code")
        output["original"] = get("original.name")
        output["original_code"] = get("original.code")

        return output

    @property
    def dates(self) -> Dict:
        output: Dict = OrderedDict()
        data: Dict = {}

        if hasattr(self, "header"):
            data = self.header.get("dates")

        get = functools.partial(query_dict, data=data)

        output["first_prod"] = get("production_start.standard")
        output["last_prod"] = get("production_stop.standard")
        output["first_oil"] = get("oil_start.standard")
        output["first_gas"] = get("gas_start.standard")
        output["first_water"] = get("water_start.standard")
        output["ihs_last_update"] = get("last_update.standard")

        return output

    @property
    def gatherers(self) -> Dict:
        output: Dict = OrderedDict()
        data: Dict = {}

        if hasattr(self, "header"):
            data = self.header.get("latest_gatherers")

        get = functools.partial(query_dict, data=data)

        output["liquid_name"] = get("liquid.alternate")
        output["liquid_alias"] = get("liquid.name")
        output["gas_name"] = get("gas.alternate")
        output["gas_alias"] = get("gas.name")

        return output

    @property
    def production_header(self) -> Dict:
        output: Dict = OrderedDict()
        data: Dict = {}
        wellbore: Dict = {}

        if hasattr(self, "header"):
            data = self.header

        if hasattr(self, "wellbore"):
            wellbore = self.wellbore

        get = functools.partial(query_dict, data=data)

        output["api10"] = self.api10
        output["entity"] = self.identification
        output["last_update_at"] = self.last_update_at
        output["name"] = get("designation.name")
        output["hole_direction"] = query_dict("header.designation.code", wellbore)
        output["county_name"] = get("geopolitical.county.name")
        output["county_code"] = get("geopolitical.county.code")
        output["state_name"] = get("geopolitical.province_state.name")
        output["state_code"] = get("geopolitical.province_state.code")
        output["region_name"] = get("geopolitical.region.name")
        output["operator_name"] = get("operators.current.name")
        output["operator_alias"] = get("operators.current.alternate")

        output["products"] = get("products.primary.code")
        output["production_type"] = get("type.name")
        output["product_primary"] = get("products.primary.name")

        output["perf_upper"] = get("depths.perforation_uppermost.value")
        output["perf_upper_uom"] = get("depths.perforation_uppermost.uom")
        output["perf_lower"] = get("depths.perforation_lowermost.value")
        output["perf_lower_uom"] = get("depths.perforation_lowermost.uom")
        output["well_counts"] = get("wells")

        output["dates"] = self.dates
        output["statuses"] = self.statuses
        output["gatherers"] = self.gatherers

        return output

    @property
    def production_monthly(self) -> List:
        output: List = []
        years: Dict = {}

        if hasattr(self, "production"):
            years = self.production.get("year")

        for year in years:
            yr = year.get("number")

            for month in year.get("month", {}):
                out = {}
                get = functools.partial(query_dict, data=month)

                mo = month.get("number", None)
                last_day = month.get("last_day", None)

                out["year"] = yr
                out["month"] = mo
                out["last_day"] = last_day
                out["first_date"] = datetime(year=yr, month=mo, day=1)
                out["last_date"] = datetime(year=yr, month=mo, day=last_day)
                out["total_liquid"] = get("total_liquid.value")
                out["total_liquid_uom"] = get("total_liquid.uom")
                out["oil"] = get("oil.value")
                out["oil_uom"] = get("oil.uom")
                out["total_gas"] = get("total_gas.value")
                out["total_gas_uom"] = get("total_gas.uom")
                out["casinghead_gas"] = get("casinghead_gas.value")
                out["casinghead_gas_uom"] = get("casinghead_gas.uom")
                out["water"] = get("water.value")
                out["water_uom"] = get("water.uom")
                out["gor"] = get("ratios.gas_oil.value")
                out["gor_uom"] = get("ratios.gas_oil.uom")
                out["water_cut"] = get("ratios.water_cut")
                out["well_count"] = get("wells.total")
                out["oil_well_count"] = get("wells.oil")

                output.append(out)

        return output


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config
    from api.models import ProductionHorizontal

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    model = ProductionHorizontal
    api14 = "42461409160000"
    m = model.objects.get(api14=api14)  # pylint: disable=no-member

    # vertical = "42383362060000"
    x = model.get(api14=api14)[0]
    dir(x)
    x.production_monthly
