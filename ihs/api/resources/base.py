import logging
from typing import Dict, Tuple, List, Optional
import random

from flask import Blueprint, url_for
from flask_mongoengine import Document as Model
from flask_restful import Api, Resource, request
from marshmallow import Schema


from api.helpers import paginate

logger = logging.getLogger(__name__)


class TestResource(Resource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        return request.args, 200


class HealthCheck(Resource):
    def get(self) -> Tuple[str, int]:  # type: ignore
        return "ok", 200


# class SiteMap(Resource):
#     def has_no_empty_params(self, rule):
#         defaults = rule.defaults if rule.defaults is not None else ()
#         arguments = rule.arguments if rule.arguments is not None else ()
#         return len(defaults) >= len(arguments)

#     def get(self):
#         links = []
#         for rule in app.url_map.iter_rules():
#             # Filter out rules we can't navigate to in a browser
#             # and rules that require parameters
#             if "GET" in rule.methods and self.has_no_empty_params(rule):
#                 url = url_for(rule.endpoint, **(rule.defaults or {}))
#                 links.append((url, rule.endpoint))


class DataResource(Resource):
    model: Model = None
    schema: Schema = None  # type: ignore

    def _get(self, **kwargs) -> Dict:
        logger.debug(f"{kwargs}")
        if kwargs.pop("paginate", False):
            result = paginate(self.model, self.schema, **kwargs)
        else:
            # only = kwargs.get("only", None)
            result = self.model.get(**kwargs)
            logger.debug(f"found {len(result)} record(s)")
            result = {"data": self.schema.dump(result)}
            result = {"status": "success", **result}

            if not result.get("data"):
                result["status"] = "not_found"

        return result


class SampleResource(DataResource):
    # hole_dir: HoleDirection = None
    id_model: Model = None
    primary_key_name: str = None  # type: ignore

    def _get_ids(self, area: Optional[str] = None) -> List[str]:
        if not area:
            # get random area that has wells
            areas = [x.name for x in self.id_model.objects(count__gt=0).all()]
            area = random.choice(areas)
        logger.debug(f"random area selection: {area}")
        return self.id_model.objects(name=area).get().ids

    def get(self) -> Tuple[Dict, int]:  # type: ignore
        n = request.args.get("n")
        frac = request.args.get("frac")
        area = request.args.get("area")

        ids = self._get_ids(area=area)

        if frac:
            n = int(float(frac) * len(ids))
        elif n:
            n = int(n)
        else:
            return {"status": "missing_argument"}, 400

        # logger.warning(ids)
        if ids:
            n = n if n < len(ids) else len(ids)
            ids = random.sample(ids, k=n)
            query_kwargs = {f"{self.primary_key_name}__in": ids}
            return self._get(**query_kwargs), 200

        else:
            return {"status": "no_ids_found"}, 400


class IDResource(DataResource):
    def get(self, area: str) -> Tuple[Dict, int]:
        return self._get(name=area), 200


class IDListResource(IDResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        areas = request.args.get("areas")
        exclude = request.args.get("exclude")
        # only = request.args.get("only")

        if exclude:
            exclude = str(exclude).split(",")

        if areas:
            return self._get(name__in=str(areas).split(","), exclude=exclude), 200
        else:
            return self._get(exclude=exclude), 200


blueprint = Blueprint("root", __name__)
api = Api(blueprint)

api.add_resource(HealthCheck, "/health")
# api.add_resource(SiteMap, "/routes")
