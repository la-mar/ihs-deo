import functools
from collections import OrderedDict

from marshmallow import Schema, fields

from api.schema.base import BaseSchema


class IDListSchema(BaseSchema):

    name = fields.Str()
    ids = fields.List(fields.Str())
    count = fields.Int()
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
    m = model.objects.get(name=name)
    sch = IDListSchema()
    sch.dump(m)
