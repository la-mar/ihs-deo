import functools
from collections import OrderedDict

from marshmallow import Schema, fields

from api.schema.base import BaseSchema


class WellRequestSchema(BaseSchema):

    area_name = fields.Str()
    api14 = fields.List(fields.Str())
    last_update_at = fields.DateTime()


if __name__ == "__main__":
    # pylint: disable=no-member
    from ihs import create_app
    from config import get_active_config
    from api.models import WellMasterHorizontal

    app = create_app()
    app.app_context().push()
    conf = get_active_config()
    model = WellMasterHorizontal
    name = "tx-mitchell"
    api14 = "42461409160000"
    api14s = [api14, "42461411260000", "42461411600000"]
    sch = WellRequestSchema()
    sch.dump(dict(area_name=name, api14=api14s))
