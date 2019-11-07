from typing import Dict, Optional
import logging
import os
from datetime import datetime, timedelta
from time import sleep
from copy import copy
from urllib.parse import urlparse

import requests
import logging

from collector.util import retry

logger = logging.getLogger(__name__)

# r = Request("GET", "https://api.example.com/v1/path/1/subpath/2/values")


class Request(requests.Request):
    """ An objects specifying a single request to be made to an endpoint."""

    _session = None
    _max_attempts = 3
    attempts = 0
    timeouts = 0

    def __init__(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        session: requests.Session = None,
    ):

        super().__init__(method)
        self.method = method
        self.url = url
        self.headers = headers
        self.params = params
        self._session = session

    def __repr__(self):
        params = ", ".join([f"{i[0]}={i[1]}" for i in self.params.items()])
        return f"{self.method} {self.path} {params}"

    @property
    def session(self):
        if self._session is None:
            self.session = requests.Session()
        return self._session

    @property
    def path(self):
        return urlparse(self.url).path

    @session.setter  # type: ignore
    def session(self, value):
        self._session = value

    def prepare(self):
        """Extend default prepare behavior to add a reference to an endpoint object.
        Done with the goal of passing the endpoint reference into the response object.

        Returns:
            prepared_request
        """
        prepared_request = super().prepare()
        # optionally modify exact request here
        return prepared_request

    @retry(Exception, tries=10, delay=5, backoff=2, logger=logger)
    def get(self):
        return self.session.get(self.url, headers=self.headers, params=self.params)


if __name__ == "__main__":

    from collector.requestor import IWellRequestor

    from collector.endpoint import Endpoint
    from config import get_active_config

    from datetime import datetime

    config = get_active_config()
    endpoints = config.endpoints
    functions = config.functions
    endpoint = endpoints.wells

    url = config.API_BASE_URL + endpoints.wells.path
    requestor = IWellRequestor(
        "req_name", endpoint, since=datetime(year=2019, month=10, day=1)
    )

    headers = requestor.headers
    params = requestor.params

    resp = requests.get(url, headers=headers, params=params)
    resp.json()
