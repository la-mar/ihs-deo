import functools
from typing import Dict

from marshmallow import Schema, fields, pre_dump

from api.schema import IPTestSchema, WellBaseSchema
from api.schema.base import BaseSchema
from util import query_dict


class WellLocationSchema(BaseSchema):
    class Meta:
        ordered = True

    lon = fields.Float(allow_none=True)
    lat = fields.Float(allow_none=True)
    crs = fields.Str()
    block = fields.Str()
    section = fields.Str()
    abstract = fields.Str()
    survey = fields.Str()
    metes_bounds = fields.Str()
    geom = fields.Dict()


class SurveyPointSchema(BaseSchema):
    md = fields.Int()
    tvd = fields.Int()
    dip = fields.Float()
    geom = fields.Dict()


class SurveySchema(BaseSchema):
    class Meta:
        ordered = True

    survey_type = fields.Str()
    survey_method = fields.Str()
    survey_end_date = fields.Date()
    survey_top = fields.Int()
    survey_top_uom = fields.Str()
    survey_base = fields.Int()
    survey_base_uom = fields.Str()
    line = fields.Dict()
    points = fields.Nested(SurveyPointSchema(many=True))
    data_source = fields.Str()

    # @pre_dump
    # def transform(self, data, **kwargs):
    #     output = super().transform(data)
    #     return {**output, **data.active_survey}


class GeomsSchema(WellBaseSchema):
    shl = fields.Nested(WellLocationSchema)
    bhl = fields.Nested(WellLocationSchema)
    pbhl = fields.Nested(WellLocationSchema)
    survey = fields.Nested(SurveySchema)

    @pre_dump
    def transform(self, data, **kwargs):
        output = super().transform(data)
        return {**output, **data.geoms, "survey": data.active_survey}


class WellElevationSchema(BaseSchema):
    class Meta:
        ordered = True

    ground = fields.Int()
    ground_uom = fields.Str()
    ground_code = fields.Str()
    kb = fields.Int()
    kb_uom = fields.Str()
    kb_code = fields.Str()


class FracParmSchema(BaseSchema):
    class Meta:
        ordered = True

    acid = fields.Int()
    acid_uom = fields.Str()
    xlink = fields.Int()
    xlink_uom = fields.Str()
    water = fields.Int()
    water_uom = fields.Str()
    slick_water = fields.Int()
    slick_water_uom = fields.Str()
    fluid_total = fields.Int()
    fluid_total_uom = fields.Str()
    sand = fields.Int()
    sand_uom = fields.Str()
    proppant_total = fields.Int()
    proppant_total_uom = fields.Str()


class WellStatusSchema(BaseSchema):
    class Meta:
        ordered = True

    current = fields.Str()
    current_code = fields.Str()
    activity = fields.Str()
    activity_code = fields.Str()


class WellDateSchema(BaseSchema):
    class Meta:
        ordered = True

    permit = fields.Date()
    permit_expiration = fields.Date()
    spud = fields.Date()
    comp = fields.Date()
    final_drill = fields.Date()
    rig_release = fields.Date()
    first_report = fields.Date()
    ihs_last_update = fields.Date()


class WellHeaderSchema(WellBaseSchema):
    class Meta:
        ordered = True

    products = fields.Str()
    county = fields.Str()
    county_code = fields.Int()
    state = fields.Str()
    state_code = fields.Int()
    operator = fields.Str()
    operator_alias = fields.Str()
    oeprator_code = fields.Str()
    operator_city = fields.Str()
    operator_original = fields.Str()
    operator_original_alias = fields.Str()
    operator_original_code = fields.Str()
    operator_original_city = fields.Str()
    basin = fields.Str()
    sub_basin = fields.Str()
    permit_number = fields.Str()
    permit_status = fields.Str()
    tvd = fields.Int()
    tvd_uom = fields.Str()
    md = fields.Int()
    md_uom = fields.Str()
    plugback_depth = fields.Int()
    plugback_depth_uom = fields.Str()
    dates = fields.Nested(WellDateSchema)
    statuses = fields.Nested(WellStatusSchema)
    elevations = fields.Nested(WellElevationSchema)
    area_rights_value = fields.Int()
    area_rights_uom = fields.Str()
    frac = fields.Nested(FracParmSchema)
    product_primary = fields.Str()
    perf_upper = fields.Int()
    perf_upper_uom = fields.Str()
    perf_lower = fields.Int()
    perf_lower_uom = fields.Str()
    perfll = fields.Int()

    # Clean up data
    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        header: Dict = {}
        engineering: Dict = {}
        if hasattr(data, "header"):
            header = data["header"]
        if hasattr(data, "engineering"):
            engineering = data["engineering"]

        get = functools.partial(query_dict, data=header)

        output = super().transform(data)
        output["county"] = get("geopolitical.county.name")
        output["county_code"] = get("geopolitical.county.code")
        output["state"] = get("geopolitical.province_state.name")
        output["state_code"] = get("geopolitical.province_state.code")
        output["products"] = get("products.objective.code")
        output["region"] = get("geopolitical.region.name")
        output["operator"] = get("operators.current.name")
        output["operator_alias"] = get("operators.current.alternate")
        output["operator_code"] = get("operators.current.code")
        output["operator_city"] = get("operators.current_city")
        output["operator_original"] = get("operators.original.name")
        output["operator_original_alias"] = get("operators.original.alternate")
        output["operator_original_code"] = get("operators.original.code")
        output["operator_original_city"] = get("operators.original_city")
        output["basin"] = get("basin.main.name")
        output["sub_basin"] = get("basin.sub_basin.name")
        output["permit_number"] = get("permit.number")
        output["permit_status"] = get("statuses.permit.name")
        output["tvd"] = get("depths.total_true_vertical.value")
        output["tvd_uom"] = get("depths.total_true_vertical.uom")
        output["md"] = get("depths.total_measured.value")
        output["md_uom"] = get("depths.total_measured.uom")
        output["plugback_depth"] = get("depths.plugback.value")
        output["plugback_depth_uom"] = get("depths.plugback.uom")
        output["area_rights_value"] = get("areas.rights.value")
        output["area_rights_uom"] = get("areas.rights.uom")

        output["product_primary"] = get("products.objective.code")

        output["perf_upper"] = query_dict(
            "completion.header.depths.top.value", data=engineering
        )
        output["perf_upper_uom"] = query_dict(
            "completion.header.depths.top.uom", data=engineering
        )

        output["perf_lower"] = query_dict(
            "completion.header.depths.base.value", data=engineering
        )
        output["perf_lower_uom"] = query_dict(
            "completion.header.depths.base.uom", data=engineering
        )

        if output["perf_upper"] and output["perf_lower"]:
            output["perfll"] = output["perf_lower"] - output["perf_upper"]
        else:
            output["perfll"] = None

        output["statuses"] = data.well_statuses or {}
        output["elevations"] = data.well_elevations or {}
        output["frac"] = data.frac or {}
        output["dates"] = data.well_dates or {}

        return output


class WellFullSchema(WellHeaderSchema):
    class Meta:
        ordered = True

    # shl = fields.Nested(WellLocationSchema)
    # bhl = fields.Nested(WellLocationSchema)
    # pbhl = fields.Nested(WellLocationSchema)
    # geoms = fields.Nested(GeomsSchema)
    ip = fields.Nested(IPTestSchema, many=True)

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:

        output = super().transform(data)
        # print(data)
        output["ip"] = data.ip_tests
        # output.update(data.geoms)

        # if hasattr(data, "geoms"):
        #     output["survey_line"] = data.geoms.get("survey_line")

        return output


class WellIPTestSchema(WellBaseSchema):
    class Meta:
        ordered = True

    ip = fields.Nested(IPTestSchema, many=True)

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        output = super().transform(data)
        output["ip"] = data.ip_tests
        return output


class WellFrac(WellBaseSchema):
    class Meta:
        ordered = True

    frac = fields.Nested(FracParmSchema)

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        output = super().transform(data)
        output["frac"] = data.frac
        return output


if __name__ == "__main__":
    # pylint: disable=no-member
    from ihs import create_app
    from config import get_active_config
    from api.models import WellHorizontal

    app = create_app()
    app.app_context().push()
    conf = get_active_config()
    model = WellHorizontal
    api14 = "42461409160000"
    m = model.objects.get(api14=api14)
    sch = WellFullSchema()

    sch.dump(m)["survey_line"]
