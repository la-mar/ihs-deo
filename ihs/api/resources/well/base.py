import logging
from typing import Dict, Tuple, Optional, List, Any
import random

from flask_restful import request
from flask import make_response

from api.resources.base import DataResource, SampleResource


logger = logging.getLogger(__name__)


class WellResource(DataResource):
    def get(self, api14: str) -> Tuple[Dict, int]:
        return self._get(api14=api14), 200


class WellListResource(WellResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        api14 = request.args.get("api14")
        api10 = request.args.get("api10")
        since = request.args.get("since")

        kwargs: Dict[str, Any] = {}

        if api10:
            kwargs["api10"] = api10

        if api14:
            kwargs["api14"] = api14

        if since:
            kwargs["ihs_last_update_date__gte"] = since

        logger.debug(f"({self.__class__.__name__}): {kwargs}")  # noqa

        if kwargs:
            return self._get(**kwargs), 200
        else:
            return {"status": "missing_argument"}, 400

    def post(self) -> Tuple[Dict, int]:
        api14 = request.args.get("api14")

        if api14:
            return self._get(paginate=True, api14__in=api14.split(","))
        else:
            return {"status": "missing_argument"}, 400
