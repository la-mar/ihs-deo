from __future__ import annotations

import logging
from time import sleep
from typing import Any, Generator, List, Union

import zeep
from zeep import xsd

import util
from collector.requestor import Requestor
from config import get_active_config

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
        self.client = self.get_client(kwargs.pop("client_type", "session"))

    @property
    def service(self):
        return self.client.service

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
