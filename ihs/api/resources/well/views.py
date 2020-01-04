from flask import Blueprint, current_app
from flask_restful import Api


import api.resources.well.horizontal as h
import api.resources.well.vertical as v
from ihs import apispec
from api.schema import IDListSchema


blueprint = Blueprint("well", __name__, url_prefix="/well")
api = Api(blueprint)

api.add_resource(h.HorizontalWellList, "/h")
api.add_resource(h.HorizontalWellIDList, "/h/ids")
api.add_resource(h.HorizontalWellIDs, "/h/ids/<area>")
api.add_resource(h.HorizontalWellHeaderList, "/h/headers")
api.add_resource(h.HorizontalWellIPTestList, "/h/ips")
api.add_resource(h.HorizontalWellSurveyList, "/h/surveys")
api.add_resource(h.HorizontalWellFracList, "/h/fracs")
api.add_resource(h.HorizontalWell, "/h/<api14>")
api.add_resource(h.HorizontalWellHeader, "/h/<api14>/header")
api.add_resource(h.HorizontalWellIPTest, "/h/<api14>/ip")
api.add_resource(h.HorizontalWellSurvey, "/h/<api14>/survey")
api.add_resource(h.HorizontalWellFrac, "/h/<api14>/frac")

api.add_resource(v.VerticalWellList, "/v")
api.add_resource(v.VerticalWellIDList, "/v/ids")
api.add_resource(v.VerticalWellIDs, "/v/ids/<area>")
api.add_resource(v.VerticalWellHeaderList, "/v/headers")
api.add_resource(v.VerticalWellIPTestList, "/v/ips")
api.add_resource(v.VerticalWellSurveyList, "/v/surveys")
api.add_resource(v.VerticalWellFracList, "/v/fracs")
api.add_resource(v.VerticalWell, "/v/<api14>")
api.add_resource(v.VerticalWellHeader, "/v/<api14>/header")
api.add_resource(v.VerticalWellIPTest, "/v/<api14>/ip")
api.add_resource(v.VerticalWellSurvey, "/v/<api14>/survey")
api.add_resource(v.VerticalWellFrac, "/v/<api14>/frac")


# @blueprint.before_app_first_request
# def register_views():
#     apispec.spec.components.schema("IDListSchema", schema=IDListSchema)
#     apispec.spec.path(view=v.WellIDs, app=current_app)
