from marshmallow import Schema, fields, pre_dump

from api.schema import WellBaseSchema
from api.schema.base import BaseSchema


class SurveyPointSchema(BaseSchema):
    md = fields.Int()
    tvd = fields.Int()
    geom = fields.Dict()


class SurveySchema(WellBaseSchema):
    class Meta:
        ordered = True

    survey_type = fields.Str()
    survey_method = fields.Str()
    survey_end_date = fields.Date()
    survey_top = fields.Int()
    survey_top_uom = fields.Str()
    survey_base = fields.Int()
    survey_base_uom = fields.Str()
    survey_line = fields.Dict()
    survey_points = fields.Nested(SurveyPointSchema(many=True))
    data_source = fields.Str()

    @pre_dump
    def transform(self, data, **kwargs):
        output = super().transform(data)
        return {**output, **data.active_survey}


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
    wh = SurveySchema()
    wh.dump(m)

