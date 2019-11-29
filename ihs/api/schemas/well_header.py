from collections import OrderedDict
from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    pre_dump,
    post_dump,
    post_load,
    ValidationError,
)

from util import query_dict as get
from api.schemas import WellBaseSchema


class WellLocationSchema(Schema):

    lon = fields.Float()
    lat = fields.Float()
    crs = fields.Str()
    block = fields.Str()
    section = fields.Int()
    abstract = fields.Int()
    survey = fields.Str()
    metes_bounds = fields.Str()


class WellHeaderSchema(WellBaseSchema):
    class Meta:
        ordered = True

    oeprator_code = fields.Str()
    operator_city = fields.Str()
    operator_original_name = fields.Str()
    operator_original_alias = fields.Str()
    operator_original_code = fields.Str()
    operator_original_city = fields.Str()
    basin_name = fields.Str()
    sub_basin_name = fields.Str()
    permit_number = fields.Str()
    permit_status = fields.Str()
    tvd = fields.Int()
    tvd_uom = fields.Str()
    md = fields.Int()
    md_uom = fields.Str()
    plugback_depth = fields.Int()
    plugback_depth_uom = fields.Str()
    permit_date = fields.Date()
    permit_expiration_date = fields.Date()
    spud_date = fields.Date()
    comp_date = fields.Date()
    final_drill_date = fields.Date()
    rig_release_date = fields.Date()
    first_report_date = fields.Date()
    ihs_last_update_date = fields.Date()
    elevation_ground = fields.Int()
    elevation_ground_uom = fields.Str()
    elevation_ground_code = fields.Str()
    elevation_kb = fields.Int()
    elevation_kb_uom = fields.Str()
    elevations_kb_code = fields.Str()
    status_current_name = fields.Str()
    status_current_code = fields.Str()
    status_activity_name = fields.Str()
    status_activity_code = fields.Str()
    area_rights_value = fields.Int()
    area_rights_uom = fields.Str()
    data_source = fields.Str()
    shl = fields.Nested(WellLocationSchema)
    bhl = fields.Nested(WellLocationSchema)
    pbhl = fields.Nested(WellLocationSchema)

    # Clean up data
    @pre_dump
    def transform(self, data, **kwargs):
        output = OrderedDict()
        header = data.header

        output["api14"] = data.api14
        output["api10"] = data.api10
        output["last_update_date"] = data.last_update

        output["well_name"] = get("designation.name", header)
        output["well_number"] = get("number", header)
        output["products"] = get("products.objective.code", header)
        output["hole_direction"] = get(
            "drilling.hole_direction.designation.code", header
        )
        output["county_name"] = get("geopolitical.county.name", header)
        output["county_code"] = get("geopolitical.county.code", header)
        output["state_name"] = get("geopolitical.province_state.name", header)
        output["state_code"] = get("geopolitical.province_state.code", header)
        output["region_name"] = get("geopolitical.region.name", header)
        output["operator_name"] = get("operators.current.name", header)
        output["operator_alias"] = get("operators.current.alternate", header)
        output["operator_code"] = get("operators.current.code", header)
        output["operator_city"] = get("operators.current_city", header)
        output["operator_original_name"] = get("operators.original.name", header)
        output["operator_original_alias"] = get("operators.original.alternate", header)
        output["operator_original_code"] = get("operators.original.code", header)
        output["operator_original_city"] = get("operators.original_city", header)
        output["basin_name"] = get("basin.main.name", header)
        output["sub_basin_name"] = get("basin.sub_basin.name", header)
        output["permit_number"] = get("permit.number", header)
        output["permit_status"] = get("statuses.permit.name", header)
        output["tvd"] = get("depths.total_true_vertical.value", header)
        output["tvd_uom"] = get("depths.total_true_vertical.uom", header)
        output["md"] = get("depths.total_measured.value", header)
        output["md_uom"] = get("depths.total_measured.uom", header)
        output["plugback_depth"] = get("depths.plugback.value", header)
        output["plugback_depth_uom"] = get("depths.plugback.uom", header)

        # * dates
        output["permit_date"] = get("date.permit.standard", header)
        output["permit_expiration_date"] = get("dates.permit_expiry.standard", header)
        output["spud_date"] = get("dates.spud.standard", header)
        output["comp_date"] = get("dates.completion.standard", header)
        output["final_drill_date"] = get("dates.final_drilling.standard", header)
        output["rig_release_date"] = get("dates.rig_release.standard", header)
        output["first_report_date"] = get("dates.first_report.standard", header)
        output["ihs_last_update_date"] = get("dates.last_update.standard", header)

        # * elevations
        output["elevation_ground"] = get("elevations.ground.value", header)
        output["elevation_ground_uom"] = get("elevations.ground.uom", header)
        output["elevation_ground_code"] = (
            get("elevations.ground.reference_code", header) or "GR"
        )
        output["elevation_kb"] = get("elevations.kelly_bushing.value", header)
        output["elevation_kb_uom"] = get("elevations.kelly_bushing.uom", header)
        output["elevation_kb_code"] = (
            get("elevations.kelly_bushing.code", header) or "KB"
        )

        # * statuses
        output["status_current_name"] = get("statuses.current.name", header)
        output["status_current_code"] = get("statuses.current.code", header)
        output["status_activity_name"] = get("statuses.activity.name", header)
        output["status_activity_code"] = get("statuses.activity.code", header)

        # * rights
        output["area_rights_value"] = get("areas.rights.value", header)
        output["area_rights_uom"] = get("areas.rights.uom", header)
        output["data_source"] = "IHS"

        # * locations
        output.update(data.well_locations)

        return output

    # We add a post_dump hook to add an envelope to responses
    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        key = "data" if many else "data"
        return {key: dict(data)}


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config
    from api.models import WellHorizontal

    app = create_app()
    app.app_context().push()
    conf = get_active_config()
    model = WellHorizontal
    api14 = "42461409160000"
    m = model.objects.get(api14=api14)
    wh = WellHeaderSchema()
    wh.dump(m)
    # get("geopolitical.county.name", m.header)
