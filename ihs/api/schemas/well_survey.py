from collections import OrderedDict
import functools
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

from util import query_dict
from api.schemas import WellBaseSchema


class SurveyPointSchema(Schema):
    md = fields.Int()
    md_uom = fields.Str()
    tvd = fields.Int()
    tvd_uom = fields.Str()
    lon = fields.Float()
    lat = fields.Float()


class WellSurveySchema(WellBaseSchema):
    class Meta:
        ordered = True

    survey_type = fields.Str()
    survey_method = fields.Str()
    survey_end_date = fields.Date()
    survey_top = fields.Int()
    survey_top_uom = fields.Str()
    survey_base = fields.Int()
    survey_base_uom = fields.Str()
    points = fields.Nested(SurveyPointSchema(many=True))
    data_source = fields.Str()

    # Clean up data
    @pre_dump
    def transform(self, data, **kwargs):
        return {**data.well_header, **data.active_survey}

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
    m = model.objects.get(api14=api14)  # pylint: disable=no-member
    wh = WellSurveySchema()
    wh.dump(m)
    # get("geopolitical.county.name", m.header)
