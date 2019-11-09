from __future__ import annotations

import logging
import urllib.parse
from datetime import date, datetime, timedelta
from typing import Dict, Generator, List, Union, Any

import zeep
from zeep import xsd

from collector.endpoint import Endpoint
from collector.requestor import Requestor
from config import get_active_config
import collector.util as util

logger = logging.getLogger(__name__)
conf = get_active_config()


class IHSHeaders:
    """ Handles authorization and initiates requests to the SOAP service"""

    _url_path = "Enerdeq/Schemas/Header"
    _confheaders = conf.api_params.get("headers")
    _soapheaders = None

    def __init__(self, base_url: str):
        self.base_url = base_url

    @property
    def schema_header_url(self):
        return util.urljoin(self.base_url, self._url_path)

    def make_header_element(self, name: str, value: Any = xsd.String()):
        return xsd.Element("{%s}%s" % (self.schema_header_url, name), value,)

    @property
    def soapheaders(self) -> List[xsd.ComplexType]:
        """Creates the authorization headers expected by the SOAP server. Equivalent to the following:

            SoapHeader = xsd.Element(
                "{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Header",
                xsd.ComplexType(
                    [
                        xsd.Element(
                            "{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Username",
                            xsd.String(),
                        ),
                        xsd.Element(
                            "{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Password",
                            xsd.String(),
                        ),
                        xsd.Element(
                            "{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Application",
                            xsd.String(),
                        ),
                    ]
                ),
            )
            return SoapHeader(
                        Username="USERNAME",
                        Password="PASSWORD",
                        Application="APPNAME"
                    )

        """
        if self._soapheaders is None:
            elements = [
                self.make_header_element(key) for key in self._confheaders.keys()
            ]

            SoapHeader = self.make_header_element("Header", xsd.ComplexType(elements))

            self._soapheaders = SoapHeader(**self._confheaders)

        return [self._soapheaders]


class SoapRequestor(Requestor):
    headers = conf.api_params.get("headers")
    _wsdls = conf.api_params.get("wsdls")
    _soapheaders = IHSHeaders(conf.api_params.get("base_url")).soapheaders
    _session = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = self.get_client(kwargs.pop("client_type"))

    @property
    def soapheaders(self):
        return self._soapheaders

    def get_client(self, name: str) -> zeep.Client:
        client = zeep.Client(wsdl=self.get_wsdl(name))
        client.set_default_soapheaders(self.soapheaders or [])
        return client

    def get_wsdl(self, name: str) -> str:
        """ Get a versioned path to a named wsdl file """
        return self._wsdls[name].format(version=self.endpoint.version)

    @property
    def session(self):
        if self._session is None:
            self._session = self.get_client("session")
        return self._session

    @property
    def s(self):
        """ Alias for session """
        return self.session


class Builder(SoapRequestor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def service(self):
        return self.s.service

    def connect(self) -> bool:
        """Initiate a connection to the soap service"""
        return self.s.service.Login(_soapheaders=self.soapheaders)

    def build(self, params: dict, target: dict) -> int:
        return self.service.BuildExportFromQuery(params, target)


class ExportBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="exportbuilder", *args, **kwargs)


class QueryBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="querybuilder", *args, **kwargs)


if __name__ == "__main__":

    from collector.endpoint import load_from_config

    endpoints = load_from_config(conf)

    x = IHSHeaders(conf.API_BASE_URL)

    x = ExportBuilder(conf.API_BASE_URL, endpoints.get("wells"))

    x.connect()

