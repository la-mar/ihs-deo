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
        "host": conf.database_uri() if not conf.DATABASE_URI else conf.DATABASE_URI,
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
    import api.resources.base as root
    import api.resources.well as well
    import api.resources.production as production

    # register blueprints
    app.register_blueprint(root.blueprint)
    app.register_blueprint(well.blueprint)
    app.register_blueprint(production.blueprint)


if __name__ == "__main__":
    app = create_app()
    app.app_context().push()

    db
