# pylint: disable=not-an-iterable, no-member
from typing import List, Dict, Tuple
from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
import json

# from marshmallow import (
#     Schema,
#     fields,
#     validate,
#     pre_load,
#     post_dump,
#     post_load,
#     ValidationError,
# )

from ihs.api.models import (
    WellMasterHorizontal,
    WellMasterVertical,
    WellHorizontal,
    WellVertical,
)

well_blueprint = Blueprint("well", __name__, url_prefix="/well")
api = Api(well_blueprint)


# class WellSchema(Schema):
#     name = fields.Str(dump_only=True, required=True)

#     # Clean up data
#     @pre_load
#     def process_input(self, data, **kwargs):
#         # data["email"] = data["email"].lower().strip()
#         return data

#     # We add a post_dump hook to add an envelope to responses
#     @post_dump(pass_many=True)
#     def wrap(self, data, many, **kwargs):
#         key = "users" if many else "user"
#         return {key: data}


@well_blueprint.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "success", "message": "pong!"})


class HorizontalAreasList(Resource):
    def get(self) -> Tuple[Dict, int]:
        """Get all makes"""
        response_object = {
            "status": "success",
            "data": WellMasterHorizontal.primary_key_values,
        }
        return response_object, 200


class HorizontalIDs(Resource):
    def get(self, name: str) -> Tuple[Dict, int]:
        """Get all makes"""
        response_object = {
            "status": "success",
            "data": WellMasterHorizontal.objects.get(name=name).ids,
        }
        return response_object, 200


class Well(Resource):
    def get(self, api14: str) -> Tuple[Dict, int]:
        """Get all makes"""
        response_object = {
            "status": "success",
            "data": json.loads(WellHorizontal.objects.get(api14=api14).to_json()),
        }
        return response_object, 200


class Test(Resource):
    def get(self) -> Tuple[Dict, int]:
        """Get all makes"""
        # return dir(request), 200
        return request.args, 200


api.add_resource(Test, "/test")
api.add_resource(HorizontalAreasList, "/areas")
api.add_resource(HorizontalIDs, "/ids/<name>")
api.add_resource(Well, "/<api14>")


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config

    app = create_app()
    app.app_context().push()

    conf = get_active_config()

    model = WellMasterHorizontal

    [m.to_json() for m in model.objects.only("_id")][0]

    name = "tx-mitchell"
    model.objects.get(name=name).ids

    dir(model.objects)

