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

logger = logging.getLogger(__name__)
conf = get_active_config()


class SoapRequestor(Requestor):
    headers = conf.api_params.get("headers")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IHSSoapRequestor(SoapRequestor):
    _wsdl_header_path = "Enerdeq/Schemas/Header"
    _soapheaders = None

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    @property
    def schema_header_url(self):
        return self.urljoin(self.base_url, self._wsdl_header_path)

    def make_header_element(self, name: str, value: Any = xsd.String()):
        return xsd.Element("{%s}%s" % (self.schema_header_url, name), value,)

    @property
    def soapheaders(self) -> xsd.ComplexType:
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
            elements = [self.make_header_element(key) for key in self.headers.keys()]

            SoapHeader = self.make_header_element("Header", xsd.ComplexType(elements))

            self._soapheaders = SoapHeader(**self.headers)

        return self._soapheaders


if __name__ == "__main__":

    from collector.endpoint import load_from_config

    endpoints = load_from_config(conf)

    x = IHSSoapRequestor(conf.API_BASE_URL, endpoints.get("wells"))

    self = x

