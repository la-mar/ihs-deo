from __future__ import annotations
from typing import Dict
import logging
from datetime import date, datetime

from typing import Union, List, Tuple
from collector.soap_requestor import SoapRequestor
from collector.export_parameter import ExportParameter
from config import get_active_config

conf = get_active_config()

logger = logging.getLogger(__name__)


class ExportJob:
    # TODO: Make endpoint_name required arg
    def __init__(self, job_id: str, **kwargs):
        self.job_id = job_id
        self._kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"ExportJob: {self.job_id}"

    def to_dict(self):
        return {"job_id": self.job_id, **self._kwargs}


class Builder(SoapRequestor):
    """ IHS specific builder """

    domain = conf.API_DOMAIN

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def service(self):
        return self.client.service

    def connect(self) -> bool:
        """Initiate a connection to the soap service"""
        return self.service.Login(_soapheaders=self.soapheaders)

    def build(self, params: dict, target: dict) -> str:
        return self.service.BuildExportFromQuery(params, target)

    def dtypes(self, domain: str = None) -> list:
        """ List the datadypes available to this service.

        Example:
            ['Production Allocated',
            'Production Unallocated',
            'Well',
            'Activity Data',
            'Rig Activity']
        """
        return self.service.GetDatatypes(self.domain or domain)

    def templates(self, data_type: str, domain: str = None):
        """ List the available templates

            ['EnerdeqML 1.0 Well',
            'EnerdeqML Well',
            'Excel Well Workbook (Excel 2002, 2003, 2007)',
            'Excel Well Workbook (Excel 2007, 2010)',
            'Excel Well Workbook (CSV)',
            'Well ID List',
            '297 Well (fixed field)',
            '297 Well (comma delimited)',
            'Well Header',
            'Excel Directional Survey (Compatible with Excel 2003 and newer)',
            'Excel Directional Survey (Compatible with Excel 2007 and newer)',
            'Excel Directional Survey (CSV)',
            'Well Completion List',
            'Well Completion List (CSV)',
            'Geoscience Software PRODFit ASCII Export',
            'EnerdeqML Production',
            'Excel Production Workbook (Excel 2002, 2003, 2007)',
            'Excel Production Workbook (Excel 2007, 2010)',
            'Excel Production Workbook (CSV)',
            'EnerdeqML 1.0 Production',
            'Production ID List',
            '298 Production (comma delimited)',
            '298 Summary Production (comma delimited)',
            '298 Production (fixed field)',
            '298 Summary Production (fixed field)',
            'Lease Producing Well Count (Compatible with Excel 2007 and newer)',
            'Lease Producing Well Count (Compatible with Excel 2003 and newer)',
            'Lease Producing Well Count (CSV)',
            'PowerTools Production Export',
            'Powertools Production Export (comma delimited)',
            'PowerTools Summary Production Export',
            'Production Header',
            'DMP2 Production',
            'DMP2 Summary Production']
        """

        return self.service.GetExportTemplates(self.domain or domain, data_type)

    def delete_job(self, job: Union[ExportJob, str]) -> bool:

        result = False
        if isinstance(job, ExportJob):
            job = job.job_id

        try:
            result = self.service.DeleteExport(job)
            logger.info("Deleted job: %s", job)
        except Exception as e:
            logger.info("Encountered error when deleting job %s -- %s", job, e)

        return result

    def job_exists(self, job: Union[ExportJob, str]) -> bool:
        if isinstance(job, ExportJob):
            job = job.job_id
        return self.service.Exists(job)

    def list_completed_jobs(self) -> List[str]:
        return self.service.GetCompleteExports()

    def delete_all_jobs(self):
        for job in eb.list_completed_jobs():
            eb.delete_job(job)


class ExportBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="exportbuilder", *args, **kwargs)

    def submit(
        self, export_param: ExportParameter, metadata: dict = None
    ) -> Union[ExportJob, None]:

        try:
            job_id = self.build(export_param.params, export_param.target)
            return ExportJob(
                job_id=job_id, **{**(metadata or {}), **dict(export_param)}
            )
        except Exception as e:
            logger.warning(
                f"Error getting job id from service for data type {export_param.data_type} -- {e}"
                + "\nmetadata: "
                + str(metadata)
                + "\n\n"
            )
        return None


class QueryBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="querybuilder", *args, **kwargs)

    @property
    def data_type(self):  # TODO: move upstream to SoapRequestor
        return self.endpoint.options.get("data_type")


class CDExporter(QueryBuilder):

    _from_date: Union[str, None] = None
    _to_date: Union[str, None] = None

    def __init__(self, from_date: str, to_date: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_date = from_date
        self.to_date = to_date

    @property
    def from_date(self):
        return self._from_date

    @from_date.setter
    def from_date(self, value: Union[str, date, datetime]):
        self._from_date = self._date_to_string(value)

    @property
    def to_date(self):
        return self._to_date

    @to_date.setter
    def to_date(self, value: Union[str, date, datetime]):
        self._to_date = self._date_to_string(value)

    def _date_to_string(self, value: Union[date, datetime, str]) -> str:
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            value = value.strftime("%Y/%m/%d")

        return value

    def get_changes_and_deletes(
        self, page: int = None, domain: str = None, data_type: str = None,
    ) -> Tuple[Dict[str, int], str]:
        domain = domain or self.domain
        data_type = data_type or self.data_type
        page = page or 1
        result = self.service.GetChangesAndDeletes(
            DataType=data_type,
            Domain=domain,
            FromDate=self.from_date,
            ToDate=self.to_date,
            Page=page,
        )

        paging_details = {
            "page": result.PagingDetails.Page,  # current page number
            "page_count": result.PagingDetails.PageCount,  # number of records on current page
            "default_page_size": result.PagingDetails.DefaultPageSize,
            "pages": result.PagingDetails.Pages,  # number of pages in result
            "total_count": result.PagingDetails.TotalCount,  # number of records across all pages
        }

        # "PagingDetails" and "Result" are proerties of the result object defined in the backing WSDL
        return paging_details, result.Result  # type: ignore

    def get_all(self) -> List[Dict[str, Union[int, str]]]:
        """ Iterate all pages of change and delete request and return a list of records

            Example result:
                    [
                        {
                            "uwi": 42389752312018,
                            "source": "PI",
                            "sequence": 12507718,
                            "date": "2018/10/15 16:53:17",
                            "newuwi": 42389376760000,
                            "referenceuwi": null,
                            "remark": "CCC - CHANGE IC ON WELL UNDER API CONTROL (ADD)",
                            "reasoncode": 8,
                            "activecode": "Y",
                            "proprietary": "N"
                        },
                    ]

            """
        results: List[str] = []

        current_page = 1
        num_pages = 1

        while current_page <= num_pages:

            paging_details, data = self.get_changes_and_deletes(page=current_page)
            results.append(data)
            num_pages = paging_details.get("pages", 0)
            logger.info(
                "Changes and Deletes: fetched page %s of %s", current_page, num_pages
            )
            current_page = paging_details.get("page", 1) + 1

        # parse results
        parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
        parsed = [parser.parse(r) for r in results]

        # flatten nested results into a single list of records
        flattened: List = []
        for p in parsed:
            flattened += p.get("changedeleterecords", p).get("changedelete", p)
        return flattened


class ExportRetriever:
    def __init__(self, job: ExportJob, **kwargs):
        self.job = job
        self.client = ExportBuilder(**kwargs)

    @property
    def is_complete(self) -> bool:
        try:
            return self.client.service.IsComplete(self.job.job_id) is not None
        except Exception as e:
            logger.warning(f"Could not determine state of Job Id {self.job.job_id} {e}")

        return False

    def get(self) -> Union[str, None]:

        try:
            result = self.client.service.RetrieveExport(self.job.job_id)
            self.client.delete_job(self.job)
            return result
        except Exception as e:
            logger.warning(f"Failed retrieving export {self.job} -- {e}")

        return None


if __name__ == "__main__":
    # pylint: disable-all

    from config import get_active_config
    from attrdict import AttrDict
    from ihs.config import get_active_config
    from ihs import create_app, db
    from collector import Endpoint
    from util import to_json
    from collector import XMLParser

    conf = get_active_config()
    app = create_app()
    app.app_context().push()

    logging.basicConfig(level=20)

    endpoints = Endpoint.load_from_config(conf, load_disabled=True)
    endpoint = endpoints.get("well_master_horizontal")

    # eb = ExportBuilder(conf.API_BASE_URL, endpoint)
    # qb = QueryBuilder(conf.API_BASE_URL, endpoint)
    cde = CDExporter("2018/10/13", "2019/11/04", endpoint=endpoint)
    self = cde
    results = cde.get_all()

    to_json(results, "test/data/changes_and_deletes_example.json")

