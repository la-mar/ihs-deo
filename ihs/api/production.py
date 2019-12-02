# pylint: disable=not-an-iterable, no-member, arguments-differ
from typing import Dict, List, Tuple, Union, no_type_check
import logging

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

import api.schema as schemas
from api.models import (
    ProductionHorizontal,
    ProductionVertical,
    ProductionMasterHorizontal,
    ProductionMasterVertical,
)

logger = logging.getLogger(__name__)

production_blueprint = Blueprint("production", __name__, url_prefix="/production")
api = Api(production_blueprint)


class DataResource(Resource):
    data_key: Union[str, None] = None
    models: Union[List, None] = None

    @no_type_check
    def get_records(self, **kwargs) -> List[Dict]:
        for model in self.models:
            result = model.get(**kwargs)
            if result:
                return result

    def _get(self, **kwargs) -> Dict:
        data = self.get_records(**kwargs)
        logger.debug(f"retrieved data: {data}")
        if self.data_key:
            data = [getattr(d, self.data_key) for d in data]
        response_object = {
            "status": "success",
            "data": self.schema.dump(data),
        }
        if not response_object.get("data"):
            response_object["status"] = "not_found"

        return response_object


class ProductionResource(DataResource):
    models = [ProductionHorizontal, ProductionVertical]

    def get(self, identifier: str) -> Tuple[Dict, int]:
        result = self._get(api10=identifier), 200
        if not result:
            result = self._get(identifier=identifier), 200

        if not result:
            pass
            #! TODO: raise value error

        return result


class ProductionListResource(ProductionResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        api10 = request.args.get("api10")
        identifier = request.args.get("id")

        if api10:
            return self._get(api10__in=str(api10).split(",")), 200
        elif identifier:
            return self._get(identification__in=str(identifier).split(",")), 200
        else:
            pass
            #! TODO: raise value error


class IDResource(DataResource):
    models = [ProductionMasterHorizontal, ProductionMasterVertical]

    def get(self, area: str) -> Tuple[Dict, int]:
        return self._get(name=area), 200


class IDListResource(IDResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        areas = request.args.get("areas")
        return self._get(name__in=str(areas).split(",")), 200


class Production(ProductionResource):
    """ All production for an api10 or entity identifier"""

    schema = schemas.ProductionFullSchema(many=True)


class ProductionList(ProductionListResource):
    """ All production data for a list of api10s or entity identifiers """

    schema = schemas.ProductionFullSchema(many=True)


class ProductionHeader(ProductionResource):
    """ Production header for an api10 or entity identifier """

    schema = schemas.ProductionHeaderSchema(many=True)


class ProductionHeaderList(ProductionListResource):
    """ Production header for a list of api10s or entity identifiers """

    schema = schemas.ProductionHeaderSchema(many=True)


class ProductionMonthly(ProductionListResource):
    """ Monthly production for an api10 or entity identifier"""

    schema = schemas.ProductionMonthlySchema(many=True)


class ProductionMonthlyList(ProductionListResource):
    """ Monthly production only for a list of api10s or entity identifiers """

    schema = schemas.ProductionMonthlySchema(many=True)


class VerticalProductionIDs(IDResource):
    models = [ProductionMasterVertical]
    schema = schemas.IDListSchema(many=True)


class HorizontalProductionIDs(IDResource):
    models = [ProductionMasterHorizontal]
    schema = schemas.IDListSchema(many=True)


class ProductionIDList(IDListResource):
    models = [ProductionMasterHorizontal, ProductionMasterVertical]
    schema = schemas.IDListSchema(many=True)


class Test(ProductionResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        return request.args, 200


api.add_resource(Test, "/test")
api.add_resource(ProductionList, "/")
api.add_resource(Production, "/<identifier>")
api.add_resource(ProductionHeader, "/<identifier>/header")
api.add_resource(ProductionHeaderList, "/headers")
api.add_resource(ProductionMonthly, "/<identifier>/monthly")
api.add_resource(ProductionMonthlyList, "/monthly")
api.add_resource(ProductionIDList, "/ids")
api.add_resource(HorizontalProductionIDs, "/ids/h/<area>")
api.add_resource(VerticalProductionIDs, "/ids/v/<area>")


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    model = ProductionHorizontal
    api10 = "42461409160000"

    apis = [api10, "42461411260000", "42461411600000"]
    many = model.get(api10__in=apis)
