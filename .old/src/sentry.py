
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def setup_sentry(
    dsn: str,
    level: int = 10, # debug
    event_level: int = 40, # error
    release: str = __name__

):

    sentry_logging = LoggingIntegration(
        level=level, # Capture info and above as breadcrumbs
        event_level=event_level # Send errors as events
    )
    sentry_sdk.init(
        dsn= dsn,
        integrations=[sentry_logging],
        release=release
    )























