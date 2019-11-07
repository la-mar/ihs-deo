from __future__ import annotations
import logging
import os
import socket
import shutil

from dotenv import load_dotenv
import pandas as pd
import tomlkit
import yaml
from attrdict import AttrDict
from sqlalchemy.engine.url import URL

""" Optional Pandas display settings"""
pd.options.display.max_rows = None
pd.set_option("display.float_format", lambda x: "%.2f" % x)
pd.set_option("large_repr", "truncate")
pd.set_option("precision", 2)

_pg_aliases = ["postgres", "postgresql", "psycopg2", "psycopg2-binary"]
_mssql_aliases = ["mssql", "sql server"]

APP_SETTINGS = os.getenv("APP_SETTINGS", "app.config.DevelopmentConfig")
FLASK_APP = os.getenv("FLASK_APP", "app.manage.py")


def make_config_path(path: str, filename: str) -> str:
    return os.path.abspath(os.path.join(path, filename))


def load_config(path: str) -> AttrDict:
    with open(path) as f:
        return AttrDict(yaml.safe_load(f))


def get_active_config() -> AttrDict:
    return globals()[APP_SETTINGS.replace("app.config.", "")]()


def get_default_port(driver: str):
    port = None
    if driver in _pg_aliases:
        port = 5432
    elif driver in _mssql_aliases:
        port = 1433

    return port


def get_default_driver(dialect: str):
    driver = None
    if dialect in _pg_aliases:
        driver = "postgres"  # "psycopg2"
    elif dialect in _mssql_aliases:
        driver = "pymssql"

    return driver


def get_default_schema(dialect: str):
    driver = None
    if dialect in _pg_aliases:
        driver = "public"
    elif dialect in _mssql_aliases:
        driver = "dbo"

    return driver


def make_url(url_params: dict) -> URL:
    return URL(**url_params)


def _get_project_meta() -> dict:
    pyproj_path = "./pyproject.toml"
    if os.path.exists(pyproj_path):
        with open(pyproj_path, "r") as pyproject:
            file_contents = pyproject.read()
        return tomlkit.parse(file_contents)["tool"]["poetry"]
    else:
        return {}


pkg_meta = _get_project_meta()
project = pkg_meta.get("name")
version = pkg_meta.get("version")


class BaseConfig:
    """Base configuration"""

    load_dotenv(".env")

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEFAULT_COLLECTION_INTERVAL = {"hours": 1}
    ENV_NAME = os.getenv("ENV_NAME", socket.gethostname())

    """ Sentry """
    SENTRY_ENABLED = os.getenv("SENTRY_ENABLED", False)
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)
    SENTRY_LEVEL = os.getenv("SENTRY_LEVEL", logging.ERROR)
    SENTRY_EVENT_LEVEL = os.getenv("SENTRY_EVENT_LEVEL", logging.ERROR)
    SENTRY_ENV_NAME = os.getenv("SENTRY_ENV_NAME", ENV_NAME)
    SENTRY_RELEASE = f"{project}-{version}"

    """ Datadog """
    DATADOG_ENABLED = os.getenv("DATADOG_ENABLED", False)
    DATADOG_API_KEY = os.getenv("DATADOG_API_KEY", None)
    DATADOG_APP_KEY = os.getenv("DATADOG_APP_KEY", None)

    """ Config """
    CONFIG_BASEPATH = "./config"
    COLLECTOR_CONFIG_PATH = make_config_path(CONFIG_BASEPATH, "collector.yaml")
    COLLECTOR_CONFIG = load_config(COLLECTOR_CONFIG_PATH)

    """ Logging """
    LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)

    """ --------------- Sqlalchemy --------------- """

    DATABASE_DIALECT = os.getenv("DATABASE_DIALECT", "postgres")
    DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", get_default_driver(DATABASE_DIALECT))
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", get_default_port(DATABASE_DRIVER))
    DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", get_default_schema(DATABASE_DRIVER))
    DATABASE_NAME = os.getenv("DATABASE_NAME", "postgres")
    DATABASE_URL_PARAMS = {
        "drivername": DATABASE_DRIVER,
        "username": DATABASE_USERNAME,
        "password": DATABASE_PASSWORD,
        "host": DATABASE_HOST,
        "port": DATABASE_PORT,
        "database": DATABASE_NAME,
    }
    SQLALCHEMY_DATABASE_URI = str(make_url(DATABASE_URL_PARAMS))
    DEFAULT_EXCLUSIONS = ["updated_at", "inserted_at"]

    """ Celery """
    # CELERY_TIMEZONE = "US/Central"
    # BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    BROKER_URL = os.getenv("CELERY_BROKER_URL", "sqs://")
    # CELERY_RESULT_BACKEND = os.getenv(
    #     "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    # )
    # CELERY_SEND_TASK_SENT_EVENT = True
    CELERY_TASK_LIST = ["collector.tasks"]
    # CELERYD_TASK_SOFT_TIME_LIMIT = 3600
    CELERYD_TASK_TIME_LIMIT = os.getenv("CELERYD_TASK_TIME_LIMIT", 60)
    CELERY_TASK_SERIALIZER = "pickle"
    CELERY_ACCEPT_CONTENT = ["json", "pickle"]
    CELERYD_MAX_TASKS_PER_CHILD = os.getenv("CELERYD_MAX_TASKS_PER_CHILD", 1000)
    CELERYD_MAX_MEMORY_PER_CHILD = os.getenv(
        "CELERYD_MAX_MEMORY_PER_CHILD", 24000
    )  # 24MB
    CELERY_ENABLE_REMOTE_CONTROL = False  # required for sqs
    CELERY_SEND_EVENTS = False  # required for sqs
    # BROKER_TRANSPORT_OPTIONS = {
    #     "visibility_timeout": 360,
    #     "region": "us-east-1",
    #     "queue_name_prefix": "app-",
    # }
    CELERY_DEFAULT_QUEUE = "app-celery"  # sqs queue name
    # CELERYD_HIJACK_ROOT_LOGGER = False
    # CELERY_RESULT_DBURI = "db+" + SQLALCHEMY_DATABASE_URI
    # CELERY_RESULT_EXTENDED = True

    """ API """
    API_CLIENT_TYPE = os.getenv("IWELL_CLIENT_TYPE", "legacy")
    API_BASE_URL = os.getenv("IWELL_URL")
    API_CLIENT_ID = os.getenv("IWELL_CLIENT_ID")
    API_CLIENT_SECRET = os.getenv("IWELL_CLIENT_SECRET")
    API_USERNAME = os.getenv("IWELL_USERNAME")
    API_PASSWORD = os.getenv("IWELL_PASSWORD")
    API_TOKEN_PATH = os.getenv("IWELL_TOKEN_PATH")
    API_PAGESIZE = os.getenv("IWELL_PAGESIZE", 1000)
    API_HEADER_KEY = os.getenv("IWELL_HEADER_KEY", "API-HEADER-KEY")
    API_HEADER_PREFIX = os.getenv("IWELL_HEADER_PREFIX", "DEO")
    API_SYNC_WINDOW_MINUTES = os.getenv("IWELL_SYNC_WINDOW_MINUTES", 1440 * 7)

    @property
    def show(self):
        return [x for x in dir(self) if not x.startswith("_")]

    @property
    def api_params(self):
        return {
            key.lower().replace("api_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("API_")
        }

    @property
    def datadog_params(self):
        return {
            key.lower().replace("datadog_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("DATADOG_")
        }

    @property
    def sentry_params(self):
        return {
            key.lower().replace("sentry_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("SENTRY_")
        }

    @property
    def endpoints(self):
        return self.COLLECTOR_CONFIG.endpoints

    @property
    def functions(self):
        return self.COLLECTOR_CONFIG.functions

    def __repr__(self):
        """ Print noteworthy configuration items """
        hr = "-" * shutil.get_terminal_size().columns + "\n"
        tpl = "{name:>25} {value:<50}\n"
        string = ""
        string += tpl.format(name="app config:", value=APP_SETTINGS)
        string += tpl.format(name="flask app:", value=FLASK_APP)
        string += tpl.format(name="flask env:", value=self.FLASK_ENV)
        string += tpl.format(
            name="backend:", value=make_url(self.DATABASE_URL_PARAMS).__repr__()
        )
        string += tpl.format(name="broker:", value=self.BROKER_URL)
        # string += tpl.format(name="result broker:", value=self.CELERY_RESULT_BACKEND)
        string += tpl.format(name="collector:", value=self.API_BASE_URL)
        return hr + string + hr


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    # load_dotenv(".env.development")

    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG_TB_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY", "test")
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(BaseConfig):
    """Testing configuration"""

    # load_dotenv(".env.testing")

    CONFIG_BASEPATH = "./test/data"
    COLLECTOR_CONFIG_PATH = make_config_path(CONFIG_BASEPATH, "collector.yaml")
    COLLECTOR_CONFIG = load_config(COLLECTOR_CONFIG_PATH)
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3

    API_BASE_URL = "https://api.example.com/v3"
    API_CLIENT_ID = "test_client_id"
    API_CLIENT_SECRET = "test_client_secret"
    API_USERNAME = "username"
    API_PASSWORD = "password"
    API_TOKEN_PATH = "/auth"
    API_DEFAULT_PAGESIZE = 100


class CIConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    """Production configuration"""

    # load_dotenv(".env.production")
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

