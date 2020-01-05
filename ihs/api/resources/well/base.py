from typing import Dict, Tuple
import logging

from flask_restful import request
from api.resources.base import DataResource


logger = logging.getLogger(__name__)


class WellResource(DataResource):
    def get(self, api14: str) -> Tuple[Dict, int]:
        return self._get(api14=api14), 200


class WellListResource(WellResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        api14 = request.args.get("api14")
        since = request.args.get("since")

        if api14:
            return self._get(api14__in=api14.split(",")), 200
        elif since:
            return (
                self._get(paginate=True, ihs_last_update_date__gte=since),
                200,
            )
        else:
            return {"status": "missing_argument"}, 400

