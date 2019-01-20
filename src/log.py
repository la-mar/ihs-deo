""" Logger definitions """

import os
import logging.config
import yaml

def setup_logging(
    default_path='config/logging.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """

    project_dir_name = os.path.basename(os.getcwd())

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())

        config['handlers']['debug_file_handler']['filename'] \
        = config['handlers']['debug_file_handler']['filename'] \
        .format(project_dir_name = project_dir_name)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.error('test-message')
