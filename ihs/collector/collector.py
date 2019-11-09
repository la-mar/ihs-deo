from __future__ import annotations
from typing import Dict, List, Union, Any
import logging
from datetime import datetime

import pandas as pd
from flask_sqlalchemy import Model
import requests


from api.models import *
from collector.endpoint import Endpoint
from collector.request import Request
from collector.transformer import Transformer
from config import get_active_config
from collector.util import retry

logger = logging.getLogger(__name__)

config = get_active_config()


class Collector(object):
    """ Acts as the conduit for transferring newly collected data into a backend data model """

    _tf = None
    _endpoint = None
    _functions = None
    _model = None

    def __init__(
        self,
        endpoint: Endpoint,
        functions: Dict[Union[str, None], Union[str, None]] = None,
    ):
        self.endpoint = endpoint
        self._functions = functions

    @property
    def functions(self):
        if self._functions is None:
            self._functions = config.functions
        return self._functions

    @property
    def model(self):
        if self._model is None:
            self._model = self.endpoint.model
        return self._model

    @property
    def tf(self):
        if self._tf is None:
            self._tf = Transformer(
                aliases=self.endpoint.mappings.get("aliases", {}),
                exclude=self.endpoint.exclude,
                date_columns=self.model.date_columns,
            )
        return self._tf

    def transform(self, data: dict) -> pd.DataFrame:
        return self.tf.transform(data)



if __name__ == "__main__":
    from app import create_app, db
    from api.models import *
    from collector.requestor import Requestor, IWellRequestor
    from collector.endpoint import load_from_config
    import requests

    app = create_app()
    app.app_context().push()

    config = get_active_config()
    endpoints = load_from_config(config)
    endpoint = endpoints["fields"]

    c = IWellCollector(endpoint)
    c.model

    requestor = IWellRequestor(config.API_BASE_URL, endpoint, functions={})

    r2 = requests.get(
        requestor.url, headers={"Authorization": requestor.get_token()}, params={}
    )
    data = r2.json()["data"]
    c.collect(r2)

