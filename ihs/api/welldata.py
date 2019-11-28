# pylint: disable=not-an-iterable, no-member
from typing import List, Dict, Tuple
from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
import json


from ihs.api.models import (
    WellMasterHorizontal,
    WellMasterVertical,
    WellHorizontal,
    WellVertical,
)

well_blueprint = Blueprint("well", __name__, url_prefix="/well")
api = Api(well_blueprint)


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


class WellHeader(Resource):
    # header/
    pass


class WellHeaderList(Resource):
    # header/
    pass


class WellTest(Resource):
    # tests/ip_pt/[type code, header]
    pass


class WellTestList(Resource):
    # tests/ip_pt/[type code, header]
    pass


class WellSurvey(Resource):
    # surveys/borehole
    pass


class WellSurveyList(Resource):
    # surveys/borehole
    pass


class WellTreatmentSummary(Resource):
    # treatment_summary/
    pass


class WellTreatmentSummaryList(Resource):
    # treatment_summary/
    pass


class WellCompletion(Resource):
    # engineering/completion/header
    pass


class WellCompletionList(Resource):
    # engineering/completion/header
    pass


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

    model = WellHorizontal
    api14 = "42461409160000"
    m = model.objects.get(api14=api14)

    # m.content
    # dir(m)
    # dir(model.objects)

