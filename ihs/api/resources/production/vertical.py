import logging

import api.schema as schemas
from api.models import ProductionMasterVertical, ProductionVertical

from api.resources.base import IDResource, IDListResource
from api.resources.production.base import ProductionResource, ProductionListResource

logger = logging.getLogger(__name__)


class VerticalProduction(ProductionResource):
    """ All production for an api10 or entity identifier"""

    model = ProductionVertical
    schema = schemas.ProductionFullSchema(many=True)


class VerticalProductionList(ProductionListResource):
    """ All production data for a list of api10s or entity identifiers """

    model = ProductionVertical
    schema = schemas.ProductionFullSchema(many=True)


class VerticalProductionHeader(ProductionResource):
    """ Production header for an api10 or entity identifier """

    model = ProductionVertical
    schema = schemas.ProductionHeaderSchema(many=True)


class VerticalProductionHeaderList(ProductionListResource):
    """ Production header for a list of api10s or entity identifiers """

    model = ProductionVertical
    schema = schemas.ProductionHeaderSchema(many=True)


class VerticalProductionMonthly(ProductionListResource):
    """ Monthly production for an api10 or entity identifier"""

    model = ProductionVertical
    schema = schemas.ProductionMonthlySchema(many=True)


class VerticalProductionMonthlyList(ProductionListResource):
    """ Monthly production only for a list of api10s or entity identifiers """

    model = ProductionVertical
    schema = schemas.ProductionMonthlySchema(many=True)


class VerticalProductionIDs(IDResource):
    model = ProductionMasterVertical
    schema = schemas.IDListSchema(many=True)


class VerticalProductionIDList(IDListResource):
    model = ProductionMasterVertical
    schema = schemas.IDListSchema(many=True)
