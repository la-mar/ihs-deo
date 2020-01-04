from typing import Dict, Tuple
import logging

from flask_restful import request
from api.resources.base import DataResource


logger = logging.getLogger(__name__)


class ProductionResource(DataResource):
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

