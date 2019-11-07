# services/users/project/__init__.py


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from celery import Celery

from config import APP_SETTINGS

# instantiate the extensions
db = SQLAlchemy()
toolbar = DebugToolbarExtension()
migrate = Migrate()
celery = Celery()


def create_app(script_info=None):
    app = Flask(__name__)
    # set config
    # app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(APP_SETTINGS)
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

