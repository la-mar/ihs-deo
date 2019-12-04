""" Entrypoint for WSGI HTTP Server, usually gunicorn """
import loggers
from ihs import create_app

loggers.standard_config()


# gunicorn expects the app object to appear under a variable named "application"
application = create_app()
