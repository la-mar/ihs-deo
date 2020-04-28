

import logging
from datetime import datetime
import time
import random

from flask import Flask, request, g
import sentry
from pymongo.read_preferences import Nearest


import loggers
import shortuuid
from config import APP_SETTINGS, get_active_config
from ext import celery, db, toolbar
from util import ensure_list
from util.dt import utcnow
from util.jsontools import to_string

loggers.config()
sentry.load()

conf = get_active_config()

logger = logging.getLogger("app.access")


def create_app(script_info=None):
    app = Flask(__name__)

    # set config
    app.config.from_object(APP_SETTINGS)
    app.config["MONGODB_SETTINGS"] = {
        "db": conf.DATABASE_NAME,
        "host": conf.database_uri() if not conf.DATABASE_URI else conf.DATABASE_URI,
        "connect": False,  # prevents prefork connection
        "replicaset": conf.REPLICA_SET,
        "read_preference": Nearest()
    }

    # set up extensions
    db.init_app(app)
    toolbar.init_app(app)
    celery.config_from_object(app.config)

    configure_blueprints(app)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db, "celery": celery}

    @app.before_request
    def before_request():
        g.start = time.time()
        request.id = shortuuid.uuid()
        request.should_log = random.random() > conf.WEB_LOG_SAMPLE_FRAC  # pairs request/response logs # noqa
        request.arg_counts = {
            k: len(ensure_list(v)) for k, v in (request.args or {}).items()
        }
        request.arg_count_str = " ".join(
            [f" {k}s={v}" for k, v in request.arg_counts.items()]
        )

        if conf.WEB_LOG_REQUESTS:
            attrs = {
                "request": {
                    "request_at": utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
                    "remote_addr": request.remote_addr,
                    "method": request.method,
                    "path": request.path,
                    "query_string": request.query_string,
                    "scheme": request.scheme,
                    "referrer": request.referrer,
                    "user_agent": request.user_agent,
                    "headers": request.headers,
                    "args": request.args,
                },
            }

            if request.should_log:
                logger.info(
                    f"[{request.id}] {request.method} - {request.scheme}:{request.path}{request.arg_count_str}",  # noqa
                    extra=attrs,
                )

    @app.after_request
    def after_request(response):
        """ Logging after every request. """

        now = time.time()
        duration = round(now - g.start, 2)

        if conf.WEB_LOG_RESPONSES:
            attrs = {
                "request": {
                    "request_id": request.id,
                    "remote_addr": request.remote_addr,
                    "method": request.method,
                    "path": request.path,
                    "query_string": request.query_string,
                    "scheme": request.scheme,
                    "referrer": request.referrer,
                    "user_agent": request.user_agent,
                    "headers": request.headers,
                    "args": request.args,
                    "arg_counts": request.arg_counts,
                    "duration": duration,
                },
                "response": {
                    "status": response.status,
                    "status_code": response.status_code,
                    "content_length": response.content_length,
                },
            }

        if request.should_log:
            logger.info(
                f"[{request.id}] RESPONSE - {request.scheme}:{request.path}{request.arg_count_str} -> {response.status} ({duration}s)",  # noqa
                extra=attrs,
            )

        return response

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
    loggers.loggers()
    al = logging.getLogger("app")
    dir(al)
