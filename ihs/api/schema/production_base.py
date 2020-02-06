# pylint: disable=unused-argument

import functools
from datetime import timezone
from typing import Dict

from marshmallow import Schema, fields, pre_dump

from api.schema.base import BaseSchema
from api.schema.validators import length_is_10, length_is_14
from util import query_dict


class ProductionBaseSchema(BaseSchema):
    class Meta:
        ordered = True

    api10 = fields.Str(required=True, validate=length_is_10)
    entity = fields.Str(required=True)
    last_update_at = fields.AwareDateTime(default_timezone=timezone.utc)
    hole_direction = fields.Str()

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        output: Dict = {}

        if hasattr(data, "production_header"):
            output = data.production_header

        return output
