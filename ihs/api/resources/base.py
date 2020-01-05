from typing import Dict, Tuple
import logging

from flask import Blueprint
from flask_restful import Resource, request, Api
from flask_mongoengine import Document as Model
from marshmallow import Schema

from api.helpers import paginate

logger = logging.getLogger(__name__)


class TestResource(Resource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        return request.args, 200


class HealthCheck(Resource):
    def get(self) -> Tuple[str, int]:  # type: ignore
        return "ok", 200


class DataResource(Resource):
    model: Model = None
    schema: Schema = None  # type: ignore

    def _get(self, **kwargs) -> Dict:
        logger.debug(f"{kwargs}")
        if kwargs.pop("paginate", False):
            result = paginate(self.model, self.schema, **kwargs)
        else:
            result = self.model.get(**kwargs)
            logger.debug(f"found {len(result)} record(s)")
            result = {"data": self.schema.dump(result)}

        response_object = {"status": "success", **result}

        if not response_object.get("data"):
            response_object["status"] = "not_found"

        return response_object


class IDResource(DataResource):
    def get(self, area: str) -> Tuple[Dict, int]:
        return self._get(name=area), 200


class IDListResource(IDResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        areas = request.args.get("areas")
        if areas:
            return self._get(name__in=str(areas).split(",")), 200
        else:
            return {"status": "missing_argument"}, 400


blueprint = Blueprint("root", __name__)
api = Api(blueprint)

api.add_resource(HealthCheck, "/health")
