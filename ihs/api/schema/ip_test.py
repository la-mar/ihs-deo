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


class IPTestSchema(Schema):
    class Meta:
        ordered = True

    type_code = fields.Str()
    test_number = fields.Int()
    test_date = fields.Date()
    test_method = fields.Str()
    completion = fields.Int()
    oil = fields.Int()
    oil_uom = fields.Str()
    gas = fields.Int()
    gas_uom = fields.Str()
    water = fields.Int()
    water_uom = fields.Str()
    choke = fields.Str()
    depth_top = fields.Int()
    depth_top_uom = fields.Str()
    depth_base = fields.Int()
    depth_base_uom = fields.Str()
    sulfur = fields.Str()
    oil_gravity = fields.Float()
    oil_gravity_uom = fields.Str()
    gor = fields.Int()
    gor_uom = fields.Str()
    perf_upper = fields.Int()
    perf_upper_uom = fields.Str()
    perf_lower = fields.Int()
    perf_lower_uom = fields.Str()
    perfll = fields.Int()
    perfll_uom = fields.Str()

    # Clean up data
    @pre_dump
    def transform(self, data, **kwargs) -> list:
        if hasattr(data, "ip_tests"):
            return data.ip_tests
        else:
            return data


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
    sch = IPTestSchema()
    sch.dump(m.ip_tests, many=True)

