import logging

import api.schema as schemas
from api.models import ProductionHorizontal, ProductionMasterHorizontal
from api.resources.base import IDListResource, IDResource
from api.resources.production.base import ProductionListResource, ProductionResource

logger = logging.getLogger(__name__)


class HorizontalProduction(ProductionResource):
    """ All production for an api10 or entity identifier"""

    model = ProductionHorizontal
    schema = schemas.ProductionFullSchema(many=True)


class HorizontalProductionList(ProductionListResource):
    """ All production data for a list of api10s or entity identifiers """

    model = ProductionHorizontal
    schema = schemas.ProductionFullSchema(many=True)


class HorizontalProductionHeader(ProductionResource):
    """ Production header for an api10 or entity identifier """

    model = ProductionHorizontal
    schema = schemas.ProductionHeaderSchema(many=True)


class HorizontalProductionHeaderList(ProductionListResource):
    """ Production header for a list of api10s or entity identifiers """

    model = ProductionHorizontal
    schema = schemas.ProductionHeaderSchema(many=True)


class HorizontalProductionMonthly(ProductionListResource):
    """ Monthly production for an api10 or entity identifier"""

    model = ProductionHorizontal
    schema = schemas.ProductionMonthlySchema(many=True)


class HorizontalProductionMonthlyList(ProductionListResource):
    """ Monthly production only for a list of api10s or entity identifiers """

    model = ProductionHorizontal
    schema = schemas.ProductionMonthlySchema(many=True)


class HorizontalProductionIDs(IDResource):
    model = ProductionMasterHorizontal
    schema = schemas.IDListSchema(many=True)


class HorizontalProductionIDList(IDListResource):
    model = ProductionMasterHorizontal
    schema = schemas.IDListSchema(many=True)
