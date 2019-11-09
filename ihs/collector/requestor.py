from __future__ import annotations
from typing import Dict, List, Union, Generator
import logging
from datetime import datetime, timedelta, date

from attrdict import AttrDict
import pandas as pd
import requests
from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session


from config import get_active_config
from collector.token_manager import TokenManager
from collector.request import Request
from collector.endpoint import Endpoint

logger = logging.getLogger(__name__)
conf = get_active_config()


class Requestor(object):
    window_timedelta = timedelta(days=1)
    sync_epoch = datetime(year=1970, month=1, day=1)
    functions: Dict[str, str] = {}
    headers: Dict[str, str] = conf.api_params.get("headers")
    params: Dict[str, str] = {}

    def __init__(
        self, base_url: str, endpoint: Endpoint, *args, **kwargs,
    ):

        self.base_url = base_url
        self.endpoint = endpoint
        self.headers = kwargs.get("headers") or self.headers
        self.params = kwargs.get("params") or self.params
        self.functions = kwargs.get("functions") or self.functions
        self._session = None
        self.requests: list = []
        self.responses: list = []


class RestRequestor(Requestor):
    window_timedelta = timedelta(days=1)
    sync_epoch = datetime(year=1970, month=1, day=1)
    functions: Dict[str, str] = {}
    headers: Dict[str, str] = {}
    params: Dict[str, str] = {}

    def __init__(
        self,
        base_url: str,
        endpoint: Endpoint,
        functions: dict = None,
        headers: dict = None,
        params: dict = None,
    ):
        super().__init__(
            base_url, endpoint, functions=functions, headers=headers, params=params
        )
        self.token_manager = TokenManager.from_app_config()

    def __repr__(self):
        return f"({self.endpoint.name})  {self.url} -> {self.model}"

    def __iter__(self) -> Generator:
        for r in self.requests:
            yield r

    @property
    def url(self):
        return self.urljoin(self.base_url, self.path)

    @property
    def path(self):
        return self.endpoint.path

    @property
    def model(self):
        """ Making requests on behalf of this model """
        return self.endpoint.model

    @property
    def session(self):
        if self._session is None:
            self.session = requests.Session()
        return self._session

    @property
    def s(self):
        """ Alias for session """
        return self.session

    @session.setter  # type: ignore
    def session(self, value):
        self._session = value

    def get_token(self, force_refresh=False):
        return self.token_manager.get_token(force_refresh=force_refresh)

    def get_function(
        self,
        func_name: str,
        value: Union[int, str, float] = None,
        value2: Union[int, str, float] = None,
        values: list = None,
    ) -> str:
        """Create a url fragment using the specified function

        Arguments:
            name {str} -- parameter name
            value {str} -- parameter value
            value2 {str} -- parameter value
            values {list} -- parameter value

        Returns:
            self
        """
        try:
            if not any([value, values]):
                raise ValueError

            if values:
                values = "".join(values)  # type: ignore

            return self.functions[func_name]["template"].format(  # type: ignore
                value=value, value2=value2, values=values
            )
        except KeyError:
            raise KeyError(f"Function not found: {func_name}")

        except ValueError:
            raise ValueError("One of value or values must be specified")

        except Exception as e:
            raise Exception(f"Failed to add function: {func_name} -- {e}")

    def add_param(self, field: str, value: Union[int, str, float] = None) -> Requestor:
        #! https://flask-restless.readthedocs.io/en/stable/searchformat.html
        try:
            self.params[field] = str(value)

        except Exception as e:
            raise Exception(f"Failed to add parameter: field={field} value={value}")

        return self

    def format(self, **kwargs) -> str:
        try:
            return self.url.format(**kwargs)
        except KeyError as ke:
            raise KeyError(f"Unable to format path ({self.path}) without {ke}")
        except Exception:
            raise

    def enqueue(self, headers: dict = None, params: dict = None, **kwargs) -> None:
        url = self.format(**kwargs)
        headers = headers or {}
        params = params or {}
        headers = {**self.headers, **headers}
        params = {**self.params, **params}

        r = Request("GET", url, headers=headers, params=params)
        self.requests.append(r)
        logger.debug(f"Queued request: {r}")
        return r

    def get_all(self) -> Generator:
        for r in self:
            logger.info(f"Sending request: {r}")
            yield r.get()


if __name__ == "__main__":
    from ihs import create_app, db

    from collector.endpoint import load_from_config

    logging.basicConfig()
    logger.setLevel(10)

    app = create_app()
    app.app_context().push()

    config = get_active_config()
    endpoints = load_from_config(config)
    url = config.API_BASE_URL
