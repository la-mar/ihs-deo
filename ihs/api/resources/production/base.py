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
        # related = util.to_bool(request.args.get("related", True))
        status = request.args.get("status")
        # logger.info(
        #     f"production get: id={api10 or ''}{identifier or ''} related={related} status={status}"  # noqa
        # )
        # logger.debug(
        #     {
        #         "api10": api10,
        #         "identifier": identifier,
        #         "related": related,
        #         "status": status,
        #     }
        # )

        kwargs: Dict[str, Any] = {}

        if status:
            kwargs["status"] = status
            logger.debug(f"production get: {kwargs}")  # noqa

        if identifier:
            kwargs["_id"] = identifier
            logger.debug(f"production get: {kwargs}")  # noqa

        # if related:
        #     kwargs["related"] = related
        #     logger.debug(f"production get: {kwargs}")  # noqa

        if api10:
            kwargs["api10"] = api10
            logger.debug(f"production get: {kwargs}")  # noqa

        if api14:
            kwargs["api14"] = api14
            logger.debug(f"production get: {kwargs}")  # noqa

        if entity12:
            kwargs["entity12"] = entity12
            logger.debug(f"production get: {kwargs}")  # noqa

        if entity:
            kwargs["entity"] = entity
            logger.debug(f"production get: {kwargs}")  # noqa

            # if api10:
            #     api10s = str(api10).split(",")
            #     logger.debug(f"selecting api10s: {api10s}")

            #     result = self.model.get(api10__in=api10s, only=["_id"])
            #     identifier = [x.id for x in result]
            #     logger.debug(identifier)

            #     # FIXME: Use entity12 instead of regex scan
            # if identifier:
            #     ids = (
            #         str(identifier).split(",")
            #         if isinstance(identifier, str)
            #         else identifier
            #     )
            #     first_12_only = []
            #     for x in ids:
            #         if len(x) > 12:
            #             x = x[:12]
            #         first_12_only.append(x)
            #         # first_12_only.append(re.compile(x + ".*", re.IGNORECASE))
            #     if related:
            #         logger.debug(f"selecting related: {first_12_only}")
            #         kwargs["entity12__in"] = first_12_only
            #     else:
            #         logger.debug(f"selecting ids: {ids}")
            #         kwargs["identification__in"] = ids

        logger.warning(f"production get: {kwargs}")  # noqa

        return self._get(**kwargs), 200

    def post(self) -> Tuple[Dict, int]:
        api10 = request.args.get("api10")

        if api10:
            return self._get(paginate=True, api10__in=api10.split(","))
        else:
            return {"status": "missing_argument"}, 400
