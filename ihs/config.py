# pylint: disable=invalid-envvar-default

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


""" Optional Pandas display settings"""
pd.options.display.max_rows = None
pd.set_option("display.float_format", lambda x: "%.2f" % x)
pd.set_option("large_repr", "truncate")
pd.set_option("precision", 2)

_pg_aliases = ["postgres", "postgresql", "psycopg2", "psycopg2-binary"]
_mssql_aliases = ["mssql", "sql server"]
_mongo_aliases = ["mongo", "mongodb"]

APP_SETTINGS = os.getenv("APP_SETTINGS", "ihs.config.DevelopmentConfig")
FLASK_APP = os.getenv("FLASK_APP", "ihs.manage.py")


def abs_path(path: str, filename: str) -> str:
    return os.path.abspath(os.path.join(path, filename))


def load_config(path: str) -> AttrDict:
    try:
        with open(path) as f:
            return AttrDict(yaml.safe_load(f))
    except FileNotFoundError as fe:
        print(f"Failed to load configuration: {fe}")


def get_active_config() -> AttrDict:
    return globals()[APP_SETTINGS.replace("ihs.config.", "")]()


def get_default_port(driver: str):
    port = None
    if driver in _pg_aliases:
        port = 5432
    elif driver in _mssql_aliases:
        port = 1433
    elif driver in _mongo_aliases:
        port = 27017
    return port


def get_default_driver(dialect: str):
    driver = None
    if dialect in _pg_aliases:
        driver = "postgres"  # "psycopg2"
    elif dialect in _mssql_aliases:
        driver = "pymssql"
    elif dialect in _mongo_aliases:
        driver = "mongodb"
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
    SENTRY_ENABLED = bool(os.getenv("SENTRY_ENABLED"))
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)
    SENTRY_LEVEL = os.getenv("SENTRY_LEVEL", 40)
    SENTRY_EVENT_LEVEL = os.getenv("SENTRY_EVENT_LEVEL", 40)
    SENTRY_ENV_NAME = os.getenv("SENTRY_ENV_NAME", ENV_NAME)
    SENTRY_RELEASE = f"{project}-{version}"

    """ Datadog """
    DATADOG_ENABLED = bool(os.getenv("DATADOG_ENABLED"))
    DATADOG_API_KEY = os.getenv("DATADOG_API_KEY", None)
    DATADOG_APP_KEY = os.getenv("DATADOG_APP_KEY", None)

    """ Config """
    CONFIG_BASEPATH = "./config"
    COLLECTOR_CONFIG_PATH = abs_path(CONFIG_BASEPATH, "collector.yaml")
    COLLECTOR_CONFIG = load_config(COLLECTOR_CONFIG_PATH)

    """ Logging """
    LOG_LEVEL = os.getenv("LOG_LEVEL", 20)

    """ --------------- Database --------------- """

    DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", "mongodb")
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", None)
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", None)
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", 27017)
    DATABASE_NAME = os.getenv("DATABASE_NAME", "default")
    DATABASE_AUTHENTICATION_SOURCE = "admin"
    # DATABASE_UUID_REPRESENTATION = "standard"
    # DATABASE_CONNECT = os.getenv("DATABASE_CONNECT", False)

    """ Celery """
    BROKER_URL = os.getenv("CELERY_BROKER_URL", "sqs://")
    CELERY_TASK_LIST = ["collector.tasks"]
    CELERYD_TASK_TIME_LIMIT = os.getenv("CELERYD_TASK_TIME_LIMIT", 60)
    CELERY_TASK_SERIALIZER = "pickle"
    CELERY_ACCEPT_CONTENT = ["json", "pickle"]
    CELERYD_MAX_TASKS_PER_CHILD = os.getenv("CELERYD_MAX_TASKS_PER_CHILD", 1000)
    CELERYD_MAX_MEMORY_PER_CHILD = os.getenv(
        "CELERYD_MAX_MEMORY_PER_CHILD", 24000
    )  # 24MB
    CELERY_ENABLE_REMOTE_CONTROL = False  # required for sqs
    CELERY_SEND_EVENTS = False
    CELERY_DEFAULT_QUEUE = f"{project}-celery"  # sqs queue name

    """ API """
    API_CLIENT_TYPE = os.getenv("IHS_CLIENT_TYPE", "legacy")
    API_BASE_URL = os.getenv("IHS_URL")
    API_USERNAME = os.getenv("IHS_USERNAME")
    API_PASSWORD = os.getenv("IHS_PASSWORD")
    API_APP_KEY = os.getenv("IHS_APP_KEY")
    # API_TOKEN_PATH = os.getenv("IHS_TOKEN_PATH")
    # API_PAGESIZE = os.getenv("IHS_PAGESIZE", 1000)
    # API_HEADER_KEY = os.getenv("IHS_HEADER_KEY", "API-HEADER-KEY")
    # API_HEADER_PREFIX = os.getenv("IHS_HEADER_PREFIX", "DEO")
    API_SYNC_WINDOW_MINUTES = os.getenv("IHS_SYNC_WINDOW_MINUTES", 1440 * 7)
    API_HEADERS = {
        "Username": API_USERNAME,
        "Password": API_PASSWORD,
        "Application": API_APP_KEY,
    }
    API_WSDL_DIR = abs_path(CONFIG_BASEPATH, "wsdl")
    API_WSDLS = {
        "session": abs_path(API_WSDL_DIR, "{version}/Session.wsdl"),
        "querybuilder": abs_path(API_WSDL_DIR, "{version}/QueryBuilder.wsdl"),
        "exportbuilder": abs_path(API_WSDL_DIR, "{version}/ExportBuilder.wsdl"),
    }
    API_DOMAIN = "US;"

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

    @property
    def database_params(self):
        return {
            key.lower().replace("database_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("DATABASE_")
        }

    def database_uri(self, hide_password=False, include_auth_source=True):
        db = self.database_params
        username = db.get("username")
        password = "***" if hide_password else db.get("password")
        auth_source = (
            f"?authSource={db.get('authentication_source')}"
            if include_auth_source
            else ""
        )
        return f"{db.get('driver')}://{username or ''}{':' if username is not None else ''}{password or ''}{'@' if username else ''}{db.get('host')}:{db.get('port')}/{db.get('name')}{auth_source}"

    def __repr__(self):
        """ Print noteworthy configuration items """
        hr = "-" * shutil.get_terminal_size().columns + "\n"
        tpl = "{name:>25} {value:<50}\n"
        string = ""
        string += tpl.format(name="app config:", value=APP_SETTINGS)
        string += tpl.format(name="flask app:", value=FLASK_APP)
        string += tpl.format(name="flask env:", value=self.FLASK_ENV)
        string += tpl.format(
            name="backend:",
            value=self.database_url(hide_password=True, include_auth_source=False),
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


class TestingConfig(BaseConfig):
    """Testing configuration"""

    # load_dotenv(".env.testing")

    CONFIG_BASEPATH = "./test/data"
    COLLECTOR_CONFIG_PATH = abs_path(CONFIG_BASEPATH, "collector.yaml")
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


if __name__ == "__main__":
    c = BaseConfig()