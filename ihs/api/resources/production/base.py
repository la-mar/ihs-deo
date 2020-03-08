import logging
from typing import Dict, Tuple
import re

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
        related = request.args.get("related", True)
        logger.debug({"api10": api10, "identifier": identifier, "related": related})

        if api10:
            api10s = str(api10).split(",")
            logger.debug(f"selecting api10s: {api10s}")

            result = self.model.get(api10__in=api10s, only=["_id"])
            identifier = [x.id for x in result]
            logger.debug(identifier)

        if identifier:

            ids = (
                str(identifier).split(",")
                if isinstance(identifier, str)
                else identifier
            )
            first_12_only = []
            for x in ids:
                if len(x) > 12:
                    x = x[:12]
                first_12_only.append(re.compile(x + ".*", re.IGNORECASE))
            if related:
                logger.debug(f"selecting related: {first_12_only}")
                return self._get(identification__in=first_12_only), 200
            else:
                logger.debug(f"selecting ids: {ids}")
                return self._get(identification__in=ids), 200
        else:
            pass

    def post(self) -> Tuple[Dict, int]:
        api10 = request.args.get("api10")

        if api10:
            return self._get(paginate=True, api10__in=api10.split(","))
        else:
            return {"status": "missing_argument"}, 400
