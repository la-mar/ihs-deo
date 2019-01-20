

import logging

import src.conductor
from src.log import setup_logging
from src.sentry import setup_sentry
from src.settings import LOG_CONFIG_PATH, SENTRY_KEY
from src.version import __project__, __version__, __release__

# Configure logging module
setup_logging(LOG_CONFIG_PATH)
logger = logging.getLogger(__name__)

setup_sentry(SENTRY_KEY, release = f'{__release__}')
logger.info(f'Sentry configured: {__release__}')


try:
    # src.conductor.send_production_updates()

except Exception as e:
    logger.exception(f'{__project__} exited abnormally. -- Error: {e}')


logger.info('Finished')
