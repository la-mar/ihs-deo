# pylint: disable=unused-argument
import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery


from api.apispec import APISpecExt
from config import APP_SETTINGS, project, get_active_config
import loggers
import sentry

loggers.config()
sentry.load()

conf = get_active_config()

# instantiate the extensions
db = MongoEngine()
toolbar = DebugToolbarExtension()
celery = Celery()
apispec = APISpecExt()


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

    configure_apispec(app)
    configure_blueprints(app)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():  # pylint: disable=unused-variable
        return {"app": app, "db": db, "celery": celery}

    return app


def configure_apispec(app):
    """Configure APISpec for swagger support
    """
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT",}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )


def configure_blueprints(app):
    # avoids circular import
    import api.resources.well as well
    import api.resources.production as production

    # register blueprints
    app.register_blueprint(well.blueprint)
    app.register_blueprint(production.blueprint)

