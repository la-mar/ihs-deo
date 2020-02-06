from flask import Blueprint, current_app
from flask_restful import Api

import api.resources.production.horizontal as h
import api.resources.production.vertical as v
# from ihs import apispec
from api.schema import IDListSchema

blueprint = Blueprint("production", __name__, url_prefix="/production")
api = Api(blueprint)

api.add_resource(h.HorizontalProductionList, "/h")
api.add_resource(h.HorizontalProduction, "/h/<identifier>")
api.add_resource(h.HorizontalProductionHeader, "/h/<identifier>/header")
api.add_resource(h.HorizontalProductionHeaderList, "/h/headers")
api.add_resource(h.HorizontalProductionMonthly, "/h/<identifier>/monthly")
api.add_resource(h.HorizontalProductionMonthlyList, "/h/monthly")
api.add_resource(h.HorizontalProductionIDList, "/h/ids")
api.add_resource(h.HorizontalProductionIDs, "/h/ids/<area>")

api.add_resource(v.VerticalProductionList, "/v")
api.add_resource(v.VerticalProduction, "/v/<identifier>")
api.add_resource(v.VerticalProductionHeader, "/v/<identifier>/header")
api.add_resource(v.VerticalProductionHeaderList, "/v/headers")
api.add_resource(v.VerticalProductionMonthly, "/v/<identifier>/monthly")
api.add_resource(v.VerticalProductionMonthlyList, "/v/monthly")
api.add_resource(v.VerticalProductionIDList, "/v/ids")
api.add_resource(v.VerticalProductionIDs, "/v/ids/<area>")


# # @blueprint.before_app_first_request
# # def register_views():
# #     apispec.spec.components.schema("IDListSchema", schema=IDListSchema)
# #     apispec.spec.path(view=Production, app=current_app)
