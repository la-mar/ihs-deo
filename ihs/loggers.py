# pylint: disable=protected-access

""" Logger definitions """

import numbers
from typing import Any, Mapping
import logging
import logging.config
import os
import sys
from logging import LogRecord

import json_log_formatter
import logutils.colorize

# from ddtrace import helpers

from config import get_active_config
from util.jsontools import ObjectEncoder


conf = get_active_config()


LOG_LEVELS = dict(logging._nameToLevel)
LOG_LEVELS.update(logging._levelToName)  # type: ignore
LOG_LEVELS.update({str(k): v for k, v in logging._levelToName.items()})  # type: ignore
LOG_LEVELS.setdefault("FATAL", logging.FATAL)
LOG_LEVELS.setdefault(logging.FATAL, "FATAL")  # type: ignore


def mlevel(level):
    """Convert level name/int to log level. Borrowed from celery, with <3"""
    if level and not isinstance(level, numbers.Integral):
        return LOG_LEVELS[level.upper()]
    return level


class ColorizingStreamHandler(logutils.colorize.ColorizingStreamHandler):
    """
    A stream handler which supports colorizing of console streams
    under Windows, Linux and Mac OS X.

    :param strm: The stream to colorize - typically ``sys.stdout``
                 or ``sys.stderr``.
    """

    # color names to indices
    color_map = {
        "black": 0,
        "red": 1,
        "green": 2,
        "yellow": 3,
        "blue": 4,
        "magenta": 5,
        "cyan": 6,
        "white": 7,
    }

    # levels to (background, foreground, bold/intense)
    if os.name == "nt":
        level_map = {
            logging.DEBUG: (None, "blue", True),
            logging.INFO: (None, "white", False),
            logging.WARNING: (None, "yellow", True),
            logging.ERROR: (None, "red", True),
            logging.CRITICAL: ("red", "white", True),
        }
    else:
        "Maps levels to colour/intensity settings."
        level_map = {
            logging.DEBUG: (None, "blue", False),
            logging.INFO: (None, "white", False),
            logging.WARNING: (None, "yellow", False),
            logging.ERROR: (None, "red", False),
            logging.CRITICAL: ("red", "white", True),
        }


class DatadogJSONFormatter(json_log_formatter.JSONFormatter):
    """JSON log formatter that includes Datadog standard attributes."""

    trace_enabled = False

    def format(self, record: LogRecord):
        """Return the record in the format usable by Datadog."""
        json_record = self.json_record(record.getMessage(), record)
        mutated_record = self.mutate_json_record(json_record)
        # Backwards compatibility: Functions that overwrite this but don't
        # return a new value will return None because they modified the
        # argument passed in.
        if mutated_record is None:
            mutated_record = json_record
        return self.to_json(mutated_record)

    def to_json(self, record: Mapping[str, Any]):
        """Convert record dict to a JSON string.
        Override this method to change the way dict is converted to JSON.
        """
        return self.json_lib.dumps(record, cls=ObjectEncoder)

    def json_record(self, message: str, record: LogRecord):
        """Convert the record to JSON and inject Datadog attributes."""
        record_dict = dict(record.__dict__)

        record_dict["message"] = message
        record_dict["tm.logger.library"] = "muselog"

        if "timestamp" not in record_dict:
            # UNIX time in milliseconds
            record_dict["timestamp"] = int(record.created * 1000)

        if "severity" not in record_dict:
            record_dict["severity"] = record.levelname

        # Source Code
        if "logger.name" not in record_dict:
            record_dict["logger.name"] = record.name
        if "logger.method_name" not in record_dict:
            record_dict["logger.method_name"] = record.funcName
        if "logger.thread_name" not in record_dict:
            record_dict["logger.thread_name"] = record.threadName

        # NOTE: We do not inject 'host', 'source', or 'service', as we want
        # Datadog agent and docker labels to handle that for the time being.
        # This may change.

        exc_info = record.exc_info
        try:
            if self.trace_enabled:
                # get correlation ids from current tracer context
                trace_id, span_id = [1, 2]  # helpers.get_correlation_ids()
                record_dict["dd.trace_id"] = trace_id or 0
                record_dict["dd.span_id"] = span_id or 0

            if "context" in record_dict:
                context_obj = dict()
                context_value = record_dict.get("context")
                if context_value:
                    array = context_value.replace(" ", "").split(",")
                else:
                    array = []
                for item in array:
                    key, val = item.split("=")

                    # del key from record before replacing with modified version
                    # NOTE: This is hacky. Need to provide a general purpose
                    # context-aware logger.
                    if key in record_dict:
                        del record_dict[key]

                    key = f"ctx.{key}"
                    context_obj[key] = int(val) if val.isdigit() else val
                    record_dict.update(context_obj)

                del record_dict["context"]
        except Exception:
            exc_info = sys.exc_info()

        # Handle exceptions, including those in our formatter
        if exc_info:
            # QUESTION: If exc_info was set by us, do we alter the log level?
            # Probably not, as a formatter should never be altering the record
            # directly.
            # I think that instead we should avoid code that can conveivably
            # raise exceptions in our formatter. That is not possible until we update
            # the context handling code and we can ensure helpers.get_correlation_ids()
            # will not raise any exceptions.
            if "error.kind" not in record_dict:
                record_dict["error.kind"] = exc_info[0].__name__  # type: ignore
            if "error.message" not in record_dict:
                record_dict["error.message"] = str(exc_info[1])
            if "error.stack" not in record_dict:
                record_dict["error.stack"] = self.formatException(exc_info)

        return record_dict


def logging_config(level: int, formatter: str = None) -> dict:
    # print(f"logger level: {level}")
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s()] %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "funcnames": {
                "format": "[%(name)s: %(lineno)s - %(funcName)s()] %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "layman": {"format": "%(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
            # "json": {"class": "json_log_formatter.JSONFormatter"},
            "json": {"class": "DatadogJSONFormatter"},
        },
        "handlers": {
            "console": {
                "level": level,
                "class": "loggers.ColorizingStreamHandler",  # "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "root": {"level": level, "handlers": ["console"]},
    }


def load_sentry():
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    logger = logging.getLogger()

    def setup(
        dsn: str,
        level: int = 10,  # debug
        event_level: int = 40,  # error
        env_name: str = None,
        release: str = None,
        **kwargs,
    ):

        sentry_logging = LoggingIntegration(
            level=level,  # Capture info and above as breadcrumbs
            event_level=event_level,  # Send errors as events
        )

        sentry_integrations = [
            sentry_logging,
            CeleryIntegration(),
            FlaskIntegration(),
            RedisIntegration(),
        ]

        sentry_sdk.init(
            dsn=dsn,
            release=release,
            integrations=sentry_integrations,
            environment=env_name,
        )
        logger.info(
            f"Sentry enabled with {len(sentry_integrations)} integrations: {', '.join([x.identifier for x in sentry_integrations])}"
        )

    try:
        parms = conf.sentry_params
        if (
            parms.get("enabled")
            and parms.get("dsn") is not None
            and parms.get("dsn") != ""
        ):
            setup(**parms)
            logger.info(f"Sentry enabled")
        else:
            logger.info(f"Sentry disabled")
            logger.debug(f"Sentry disabled: no DSN in sentry config")

    except Exception as e:
        logger.error(f"Failed to load Sentry configuration: {e}")


def config(verbosity: int = -1, level: int = None, formatter: str = None):

    if str(conf.sentry_params.get("enabled")).lower() == "true":
        load_sentry()

    root_logger = logging.getLogger()
    root_logger.setLevel(mlevel(conf.LOG_LEVEL))

    formatter = DatadogJSONFormatter()
    console_handler = ColorizingStreamHandler()
    console_handler.setFormatter(formatter)
    if root_logger.handlers:
        root_logger.removeHandler(root_logger.handlers[0])
    root_logger.addHandler(console_handler)


if __name__ == "__main__":

    config()
    logger = logging.getLogger()
    logger.debug("test-debug")
    logger.info("test-info")
    logger.warning("test-warning")
    logger.error("test-error")
