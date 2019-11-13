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

    domain = conf.API_DOMAIN

    def __init__(
        self,
        data_type: str,
        template_path: str,
        query_path: str,
        overwrite: bool = True,
        domain: str = None,
    ):

        self._export_filename = uuid4()
        self.data_type = data_type
        self._template_path = template_path
        self.template = self.load_xml(template_path)
        self.query_path = query_path
        self.query = self.load_xml(query_path)
        self.overwrite = overwrite
        self.domain = domain or self.domain

    def __repr__(self):
        return (
            f"ExportParameter: {self.domain}/{self.data_type} - {self.export_filename}"
        )

    @property
    def export_filename(self):
        return self._export_filename

    @staticmethod
    def load_xml(path: str):
        try:
            return util.load_xml(path)
        except FileNotFoundError as fe:
            logger.warning("Failed to load xml file %s -- %s", path, fe)
            raise

    @property
    def params(self) -> dict:
        return {
            "Domain": self.domain,
            "DataType": self.data_type,
            "Template": self.template,
            "Query": self.query,
        }

    @property
    def target(self) -> dict:
        return {"Filename": self.export_filename, "Overwrite": self.overwrite}


class ExportJob:
    def __init__(self, job_id: str, **kwargs):
        self.job_id = job_id
        self.attrs = kwargs

    def to_dict(self):
        return {"job_id": self.job_id, **self.attrs}


class ExportBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="exportbuilder", *args, **kwargs)

    def submit_job(self, export_param: ExportParameter) -> Union[str, None]:

        try:
            return self.client.service.BuildExportFromQuery(
                export_param.params, export_param.target
            )
        except Exception as e:
            print(
                f"Error getting job id from service for data type {export_param.data_type} {e}"
            )

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


class ExportRetreiver:
    def __init__(self, job: ExportJob):
        self.job = job


class QueryBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="querybuilder", *args, **kwargs)


if __name__ == "__main__":

    from collector.endpoint import load_from_config

    import sys

    endpoints = load_from_config(conf)
    endpoint = endpoints.get("wells")
    dir(endpoint)

    exportparam = ExportParameter(EnumDataType.WELL)

    x = ExportBuilder(conf.API_BASE_URL, endpoints.get("wells"))

    x.connect()

    job_id = x.submit_job(exportparam)

    if job_id is None:
        sys.exit()

    sleep_dur = conf.API__EXPORT_SLEEP_DUR

    while not x.job_is_complete(job_id):
        sleep(sleep_dur)
        print(f"Sleeping for {sleep_dur}")

    data = x.get_data(job_id)

    if data is None:
        print("bad data!")
