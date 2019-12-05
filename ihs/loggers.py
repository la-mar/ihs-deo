""" Logger definitions """

import logging
import logging.config
import os
from collections import defaultdict

import logutils.colorize

from config import get_active_config

config = get_active_config()  # noqa


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
        },
        "handlers": {
            "console": {
                "level": level,
                "class": "loggers.ColorizingStreamHandler",  # "logging.StreamHandler",
                "formatter": formatter or "verbose",
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
        parms = config.sentry_params
        if parms.get("enabled"):
            logger.info(f"Sentry Enabled")
            if parms.get("dsn") is not None and parms.get("dsn") != "":
                setup(**parms)
            else:
                logger.warning(f"Sentry disabled: no DSN in sentry config")
        else:
            logger.debug(f"Sentry disabled")

    except Exception as e:
        logger.error(f"Failed to load Sentry configuration: {e}")


def standard_config(verbosity: int = -1, level: int = None, formatter: str = None):

    levels = defaultdict(
        lambda: int(config.LOG_LEVEL),
        {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG},
    )

    logging.config.dictConfig(
        logging_config(levels[verbosity] or level or config.LOG_LEVEL, formatter)
    )
    logger = logging.getLogger()
    # logger.setLevel(levels[verbosity])
    logger.debug(
        f"Configured loggers (level: {logger.level}): {[x.name for x in logger.handlers]}"
    )

    if str(config.sentry_params.get("enabled")).lower() == "true":
        load_sentry()


if __name__ == "__main__":

    standard_config()
    logger = logging.getLogger()
    logger.debug("test-debug")
    logger.info("test-info")
    logger.warning("test-warning")
    logger.error("test-error")
