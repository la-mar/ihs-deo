import logging
from typing import Dict, Tuple, Any
import re

from flask_restful import request

from api.resources.base import DataResource
import util

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
        api14 = request.args.get("api14")
        entity = request.args.get("entity")
        entity12 = request.args.get("entity12")
        identifier = request.args.get("id")
        status = request.args.get("status")
        related = request.args.get("related")

        kwargs: Dict[str, Any] = {}

        if status:
            kwargs["status"] = status

        if identifier:
            kwargs["_id"] = identifier

        if api10:
            kwargs["api10"] = api10

        if api14:
            kwargs["api14"] = api14

        if entity12:
            kwargs["entity12"] = entity12

        if entity:
            kwargs["entity"] = entity

        if related is not None:
            related = util.to_bool(related)

        if related and not entity12:
            objs = self.model.objects(**kwargs).only("entity12").all()
            kwargs = {"entity12__in": list({x.entity12 for x in objs})}

        logger.debug(f"production get: {kwargs}")  # noqa

        return self._get(**kwargs), 200

    def post(self) -> Tuple[Dict, int]:
        api10 = request.args.get("api10")

        if api10:
            return self._get(paginate=True, api10__in=api10.split(","))
        else:
            return {"status": "missing_argument"}, 400
