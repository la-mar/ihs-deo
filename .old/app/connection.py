import os

import zeep
from zeep import xsd

# from dotenv import load_dotenv
import functools

# load_dotenv(verbose=True)

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

_SOAPHEADERS = [
    SoapHeader(
        Username=os.getenv("IHS_USERNAME"),
        Password=os.getenv("IHS_PASSWORD"),
        Application=os.getenv("IHS_APPNAME"),
    )
]


def soapheaders(func):
    """Add soap headers to the wrapped function's kwargs"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        kwargs["_soapheaders"] = _SOAPHEADERS
        value = func(*args, **kwargs)
        return value

    return wrapper


class IHSConnector(object):

    _wsdl_dir = ".old/app/wsdl"
    _domain = "US;"
    _wsdls = {
        "session": "Session.wsdl",
        "querybuilder": "QueryBuilder.wsdl",
        "exportbuilder": "ExportBuilder.wsdl",
    }
    _dtypes = ["Well", "Production Allocated"]

    def __init__(self, version: str = "v10"):
        self.version = version
        self._wsdl_path = self._wsdl_dir + f"/{self.version}/"
        self.session = zeep.Client(wsdl=self._wsdl_path + self._wsdls["session"])
        self.querybuilder = zeep.Client(
            wsdl=self._wsdl_path + self._wsdls["querybuilder"]
        )
        self.exportbuilder = zeep.Client(
            wsdl=self._wsdl_path + self._wsdls["exportbuilder"]
        )

    @soapheaders
    def login(self, **kwargs) -> bool:
        """Initiate a connection to the soap service"""
        return self.session.service.Login(_soapheaders=kwargs.pop("_soapheaders"))

    @property
    def dtypes(self) -> list:
        """list the available job datatypes"""
        return self._dtypes

    @soapheaders
    def build_export(self, params: dict, target: dict, **kwargs) -> int:
        return self.exportbuilder.service.BuildExportFromQuery(
            params, target, _soapheaders=kwargs.pop("_soapheaders")
        )

    @soapheaders
    def get_export(self, job_id: int, **kwargs):
        return self.exportbuilder.service.RetrieveExport(
            job_id, _soapheaders=kwargs.pop("_soapheaders")
        )

    @soapheaders
    def is_complete(self, job_id: int, **kwargs):
        return self.exportbuilder.service.IsComplete(
            job_id, _soapheaders=kwargs.pop("_soapheaders")
        )

    @soapheaders
    def get_count(self, query: str, datatype: str, **kwargs):
        return self.querybuilder.service.GetCount(
            query, datatype, self._domain, _soapheaders=kwargs.pop("_soapheaders")
        )


if __name__ == "__main__":

    ihs = IHSConnector()

    ihs.login()

