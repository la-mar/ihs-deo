""" Entrypoint for WSGI HTTP Server, usually gunicorn """
import loggers
from ihs import create_app



# gunicorn expects the app object to appear under a variable named "application"
application = create_app()
