import logging

from config import get_active_config

conf = get_active_config()

logger = logging.getLogger()


def load():
    if str(conf.sentry_params.get("enabled")).lower() == "true":
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.redis import RedisIntegration

        def setup(
            dsn: str,
            event_level: int = 40,  # error
            breadcrumb_level: int = 10,  # debug
            env_name: str = None,
            release: str = None,
            **kwargs,
        ):

            sentry_logging = LoggingIntegration(
                level=breadcrumb_level,  # Capture level and above as breadcrumbs
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
            logger.debug(
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
                logger.debug(f"Sentry disabled: no DSN in sentry config")

        except Exception as e:
            logger.error(f"Failed to load Sentry configuration: {e}")
