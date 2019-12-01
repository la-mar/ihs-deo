# pylint: disable=not-an-iterable, no-member
import json
from typing import Dict, Tuple, no_type_check

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

import api.schema as schemas
from api.models import WellMasterHorizontal, WellMasterVertical

id_blueprint = Blueprint("ids", __name__, url_prefix="/ids")
api = Api(id_blueprint)


class HorizontalAreasList(Resource):
    def get(self) -> Tuple[Dict, int]:
        response_object = {
            "status": "success",
            "data": WellMasterHorizontal.primary_key_values,
        }
        return response_object, 200


class HorizontalIDs(Resource):
    def get(self, name: str) -> Tuple[Dict, int]:
        response_object = {
            "status": "success",
            "data": WellMasterHorizontal.objects.get(name=name).ids,
        }
        return response_object, 200


api.add_resource(HorizontalAreasList, "/areas")
