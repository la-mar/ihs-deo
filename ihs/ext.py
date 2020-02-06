# pylint: disable=unused-argument

from celery import Celery
from flask_debugtoolbar import DebugToolbarExtension
from flask_mongoengine import MongoEngine

# instantiate the extensions
db = MongoEngine()
toolbar = DebugToolbarExtension()
celery = Celery()
