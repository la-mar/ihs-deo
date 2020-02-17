import logging
from typing import Dict, Optional
from urllib.parse import urlparse

import requests

from collector.util import retry

logger = logging.getLogger(__name__)


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

    @retry(Exception, tries=2, delay=15, backoff=2, logger=logger)
    def get(self):
        return self.session.get(self.url, headers=self.headers, params=self.params)
