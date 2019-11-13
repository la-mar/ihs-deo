from __future__ import annotations

import logging
import urllib.parse
from datetime import date, datetime, timedelta
from typing import Dict, Generator, List, Union, Any

import zeep
from zeep import xsd
from time import sleep

from collector.endpoint import Endpoint
from collector.requestor import Requestor
from config import get_active_config, EnumDataType
import util
from enum import Enum
from uuid import uuid4

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


class ExportParameter:
    """ Next step move this to be config driven """

    def __init__(self, dtype: EnumDataType):
        self.filename = uuid4()
        if dtype == EnumDataType.PRODUCTION_ALLOCATED:
            self.domain = "US"
            self.data_type = "Production Allocated"
            self.template = util.load_xml("config/templates/production.xml")
            self.query = util.load_xml("config/queries/production-driftwood.xml")
            self.overwrite = True

        if dtype == EnumDataType.WELL:
            self.domain = "US"
            self.data_type = "Well"
            self.template = util.load_xml("config/templates/well.xml")
            self.query = util.load_xml("config/queries/well-driftwood.xml")
            self.overwrite = True

    def get_param_dict(self) -> dict:
        return dict(
            {
                "Domain": self.domain,
                "DataType": self.data_type,
                "Template": self.template,
                "Query": self.query,
            }
        )

    def get_target_dict(self) -> dict:
        return dict({"Filename": self.filename, "Overwrite": self.overwrite})


class ExportBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="exportbuilder", *args, **kwargs)

    def get_job_id(self, eparam: ExportParameter) -> Union[str, None]:

        try:
            param_dict = eparam.get_param_dict()
            target_dict = eparam.get_target_dict()
            return self.client.service.BuildExportFromQuery(param_dict, target_dict)
        except Exception as e:
            print(
                f"Error getting job id from service for data type {eparam.data_type} {e}"
            )
            """NOT SURE IF WE SHOULD RETURN NONE"""
            return None

    def job_is_complete(self, job_id: str) -> bool:
        try:
            if self.client.service.IsComplete(job_id):
                return True
            return False
        except Exception as e:
            print(f"Could not determine state of Job Id {job_id} {e}")
            return False

    def get_data(self, job_id: str) -> Union[str, None]:

        try:
            return self.client.service.RetrieveExport(job_id)
        except Exception as e:
            print(e)
        """NOT SURE IF WE SHOULD RETURN NONE"""
        return None


class QueryBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="querybuilder", *args, **kwargs)


if __name__ == "__main__":

    from collector.endpoint import load_from_config

    import sys

    endpoints = load_from_config(conf)

    exportparam = ExportParameter(EnumDataType.WELL)

    x = ExportBuilder(conf.API_BASE_URL, endpoints.get("wells"))

    x.connect()

    job_id = x.get_job_id(exportparam)

    if job_id is None:
        sys.exit()

    sleep_dur = conf.API__EXPORT_SLEEP_DUR

    while not x.job_is_complete(job_id):
        sleep(sleep_dur)
        print(f"Sleeping for {sleep_dur}")

    data = x.get_data(job_id)

    if data is None:
        print("bad data!")

