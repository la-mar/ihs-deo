# pylint: disable=unused-argument
import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery

from ext import db, toolbar, celery
from config import APP_SETTINGS, project, get_active_config, version
import loggers
import sentry

loggers.config()
sentry.load()

conf = get_active_config()


def create_app(script_info=None):
    app = Flask(__name__)

    # set config
    app.config.from_object(APP_SETTINGS)
    app.config["MONGODB_SETTINGS"] = {
        "db": conf.DATABASE_NAME,
        "host": conf.database_uri(),
        "connect": False,  # prevents prefork connection
    }

    # set up extensions
    db.init_app(app)
    toolbar.init_app(app)
    celery.config_from_object(app.config)

    configure_blueprints(app)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():  # pylint: disable=unused-variable
        return {"app": app, "db": db, "celery": celery}

    return app


def configure_blueprints(app):
    # avoids circular import
    import api.resources.well as well
    import api.resources.production as production

    # register blueprints
    app.register_blueprint(well.blueprint)
    app.register_blueprint(production.blueprint)


# def configure_apispec(app):
#     """Configure APISpec for swagger support
#     """
#     # apispec.init_app(app)
#     # apispec.init_app(app, security=[{"oauth2": []}])

#     from apispec import APISpec
#     from apispec.ext.marshmallow import MarshmallowPlugin

#     app.config.setdefault("APISPEC_TITLE", project)
#     app.config.setdefault("APISPEC_VERSION", version)
#     app.config.setdefault("APISPEC_SWAGGER_URL", "/swagger")

#     app.config.setdefault("OPENAPI_VERSION", "3.0.2")
#     app.config.setdefault("APISPEC_SWAGGER_JSON_URL", "/swagger.json")
#     app.config.setdefault("APISPEC_SWAGGER_UI_URL", "/spec")
#     app.config.setdefault("SWAGGER_URL_PREFIX", None)

#     spec = APISpec(
#         title=app.config["APISPEC_TITLE"],
#         version=app.config["APISPEC_VERSION"],
#         openapi_version=app.config["OPENAPI_VERSION"],
#         plugins=[MarshmallowPlugin()],
#     )

#     app.config.setdefault("APISPEC_SPEC", spec)

#     docs.init_app(app)

#     docs.spec.components.security_scheme(
#         "oauth2",
#         {
#             "type": "oauth2",
#             "flows": {
#                 "clientCredentials": {
#                     "tokenUrl": "https://api.driftwoodenergy.com/auth"
#                 }
#             },
#             "scopes": {},
#         },
#     )
#     docs.spec.components.schema(
#         "PaginatedResult",
#         {
#             "properties": {
#                 "total": {"type": "integer"},
#                 "pages": {"type": "integer"},
#                 "next": {"type": "string"},
#                 "prev": {"type": "string"},
#             }
#         },
#     )

#     from api.resources.well.horizontal import HorizontalWell
#     from api.resources.base import DataResource

#     docs.register(HorizontalWell, blueprint="well")

