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

from api.schemas import WellBaseSchema


class IPTestSchema(WellBaseSchema):
    class Meta:
        ordered = True

    #! Add ip test fields

    # Clean up data
    @pre_dump
    def process_output(self, data, **kwargs):
        return {**data.well_header, **data.ip_tests}

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
    sch = IPTestSchema()
    sch.dump(m)
    # get("geopolitical.county.name", m.header)
