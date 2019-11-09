# services/users/project/__init__.py


import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from celery import Celery

from config import APP_SETTINGS, project, get_active_config

conf = get_active_config()

# instantiate the extensions
db = MongoEngine()
toolbar = DebugToolbarExtension()
migrate = Migrate()
celery = Celery()


def create_app(script_info=None):
    app = Flask(__name__)
    # set config
    # app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(APP_SETTINGS)
    app.config["MONGODB_SETTINGS"] = {
        "db": "ihs",
        "host": conf.database_uri(),
        # "name": "default",
    }
    # set up extensions
    db.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)
    celery.config_from_object(app.config)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db, "celery": celery}

    return app

