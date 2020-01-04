from typing import Dict
from datetime import timezone

from marshmallow import Schema, fields, pre_dump


from api.schema.validators import length_is_14, length_is_10
from api.schema import ProductionBaseSchema
from api.schema.base import BaseSchema


class WellCountSchema(BaseSchema):
    active_producing = fields.Int()
    active_total = fields.Int()
    total = fields.Int()


class ProductionDateSchema(BaseSchema):
    class Meta:
        ordered = True

    first_prod = fields.Date()
    last_prod = fields.Date()
    first_oil = fields.Date()
    first_gas = fields.Date()
    first_water = fields.Date()
    ihs_last_update = fields.Date()

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        data = data or {}
        if hasattr(data, "dates"):
            data = data.dates
        return data


class ProductionStatusSchema(BaseSchema):
    class Meta:
        ordered = True

    current = fields.Str()
    current_code = fields.Str()
    original = fields.Str()
    original_code = fields.Str()

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        data = data or {}
        if hasattr(data, "statuses"):
            data = data.statuses
        return data


class ProductionGathererSchema(BaseSchema):
    class Meta:
        ordered = True

    liquid_name = fields.Str()
    liquid_alias = fields.Str()
    gas_name = fields.Str()
    gas_alias = fields.Str()

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        data = data or {}
        if hasattr(data, "gatherers"):
            data = data.gatherers
        return data


class ProductionHeaderSchema(ProductionBaseSchema):
    class Meta:
        ordered = True

    county = fields.Str()
    county_code = fields.Int()
    state = fields.Str()
    state_code = fields.Int()
    operator = fields.Str()
    operator_alias = fields.Str()
    products = fields.Str()
    production_type = fields.Str()
    product_primary = fields.Str()
    perf_upper = fields.Str()
    perf_upper_uom = fields.Str()
    perf_lower = fields.Str()
    perf_lower_uom = fields.Str()
    dates = fields.Nested(ProductionDateSchema)
    statuses = fields.Nested(ProductionStatusSchema)
    gatherers = fields.Nested(ProductionGathererSchema)
    well_counts = fields.Nested(WellCountSchema)
    data_source = fields.Str()

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        output: Dict = {}
        header: Dict = data or {}

        if hasattr(data, "production_header"):
            header = data.production_header

        output = super().transform(header)
        output.update(header)
        return output


class ProductionMonthlyRecordSchema(BaseSchema):
    class Meta:
        ordered = True

    year = fields.Int()
    month = fields.Int()
    last_day = fields.Int()
    first_date = fields.Date()
    last_date = fields.Date()
    total_liquid = fields.Int()
    total_liquid_uom = fields.Str()
    oil = fields.Int()
    oil_uom = fields.Str()
    total_gas = fields.Int()
    total_gas_uom = fields.Str()
    casinghead_gas = fields.Int()
    casinghead_gas_uom = fields.Str()
    water = fields.Int()
    water_uom = fields.Str()
    gor = fields.Int()
    gor_uom = fields.Str()
    water_cut = fields.Float()
    well_count = fields.Int()
    oil_well_count = fields.Int()

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        data = data or {}
        if hasattr(data, "production_monthly"):
            data = data.production_monthly
        return data


class ProductionMonthlySchema(ProductionBaseSchema):
    class Meta:
        ordered = True

    production = fields.Nested(ProductionMonthlyRecordSchema, many=True)

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        output: Dict = {}
        production: Dict = {}

        if hasattr(data, "production_monthly"):
            production = data.production_monthly

        output = super().transform(data)
        output["production"] = production
        return output


class ProductionFullSchema(ProductionHeaderSchema):
    class Meta:
        ordered = True

    production = fields.Nested(ProductionMonthlyRecordSchema, many=True)

    @pre_dump
    def transform(self, data, **kwargs) -> Dict:
        output: Dict = {}
        production: Dict = {}

        if hasattr(data, "production_monthly"):
            production = data.production_monthly

        output = super().transform(data)
        output["production"] = production
        return output


if __name__ == "__main__":
    # pylint: disable=no-member
    from ihs import create_app
    from config import get_active_config
    from api.models import ProductionHorizontal

    app = create_app()
    app.app_context().push()
    conf = get_active_config()
    model = ProductionHorizontal
    api14 = "42461409160000"
    m = model.objects.get(api14=api14)
    sch = ProductionFullSchema()
    sch.dump(m)

