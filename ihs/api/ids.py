# pylint: disable=not-an-iterable, no-member
from typing import Dict, Tuple, Union, no_type_check

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

import api.schema as schemas
from api.models import WellMasterHorizontal, WellMasterVertical

id_blueprint = Blueprint("ids", __name__, url_prefix="/ids")
api = Api(id_blueprint)


class WellResource(Resource):
    data_key: Union[str, None] = None
    models = [WellMasterHorizontal, WellMasterVertical]

    @no_type_check
    def get_ids(self, **kwargs) -> List[Dict]:
        for model in self.models:
            result = model.get(**kwargs)
            if result:
                return result

    def _get(self, **kwargs) -> Dict:
        data = self.get_wells(**kwargs)
        if self.data_key:
            data = [getattr(d, self.data_key) for d in data]
        response_object = {
            "status": "success",
            "data": self.schema.dump(data),
        }
        if not response_object.get("data"):
            response_object["status"] = "not_found"

        return response_object

    def get(self, api14: str) -> Tuple[Dict, int]:
        return self._get(api14=api14), 200


class WellListResource(WellResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        api14 = request.args.get("api14")
        return self._get(api14__in=str(api14).split(",")), 200


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
