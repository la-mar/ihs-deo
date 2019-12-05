# pylint: disable=unused-argument
import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery

from api.well import well_blueprint
from api.production import production_blueprint

from config import APP_SETTINGS, project, get_active_config

conf = get_active_config()

# instantiate the extensions
db = MongoEngine()
toolbar = DebugToolbarExtension()
celery = Celery()


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

    # register blueprints
    app.register_blueprint(well_blueprint)
    app.register_blueprint(production_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():  # pylint: disable=unused-variable
        return {"app": app, "db": db, "celery": celery}

    return app

