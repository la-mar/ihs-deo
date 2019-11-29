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


class WellBaseSchema(Schema):
    class Meta:
        ordered = True

    api14 = fields.Str(required=True)
    api10 = fields.Str()
    last_update_date = fields.Date()
    well_name = fields.Str()
    well_number = fields.Str()
    products = fields.Str()
    hole_direction = fields.Str()
    county_name = fields.Str()
    county_code = fields.Str()
    state_name = fields.Str()
    state_code = fields.Str()
    operator_name = fields.Str()
    operator_alias = fields.Str()
