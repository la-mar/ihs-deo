from typing import Dict
import functools
from marshmallow import Schema, fields, pre_dump

from util import query_dict


class WellBaseSchema(Schema):
    class Meta:
        ordered = True

    api14 = fields.Str(required=True)
    api10 = fields.Str()
    last_update_date = fields.Date()
    well_name = fields.Str()
    well_number = fields.Str()
    hole_direction = fields.Str()

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        output: Dict = {}
        header: Dict = {}
        if hasattr(data, "header"):
            header = data["header"]

        get = functools.partial(query_dict, data=header)

        output["api14"] = data.api14
        output["api10"] = data.api10
        output["last_update_date"] = data.last_update
        output["well_name"] = get("designation.name")
        output["well_number"] = get("number")
        output["hole_direction"] = get("drilling.hole_direction.designation.code")

        return output
