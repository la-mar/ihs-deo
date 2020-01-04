# pylint: disable=unused-argument

from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery


# instantiate the extensions
db = MongoEngine()
toolbar = DebugToolbarExtension()
celery = Celery()

