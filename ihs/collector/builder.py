from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Dict, List, Tuple, Union
from urllib3.exceptions import ProtocolError
import zeep

from requests import ConnectionError

import metrics
from collector.export_parameter import ExportParameter
from collector.soap_requestor import SoapRequestor
from collector.xmlparser import XMLParser
from exc import CollectorError
from config import get_active_config

conf = get_active_config()

logger = logging.getLogger(__name__)

parser = XMLParser.load_from_config(conf.PARSER_CONFIG)


class ExportJob:
    # TODO: Make endpoint_name required arg
    def __init__(self, job_id: str, **kwargs):
        self.job_id = job_id
        self._kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        d = self.to_dict()
        truncated_job_id = str(self.job_id).split("-")[-1]
        name = d.get("name")
        return f"ExportJob({truncated_job_id}) {name}"

    def to_dict(self):
        return {"job_id": self.job_id, **self._kwargs}

    def limited_dict(
        self,
        limit_keys: list = [
            "endpoint",
            "task",
            "hole_direction",
            "data_type",
            "target_model",
            "source_name",
        ],
        include_job_id: bool = False,
    ):
        job_dict = {}
        for key, value in self.to_dict().items():
            if key in limit_keys:
                job_dict[key] = value
        return job_dict


class Builder(SoapRequestor):
    """ IHS specific builder """

    domain = conf.API_DOMAIN

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def service(self):
        return self.client.service

    @property
    def methods(self):
        return [x for x in dir(self.client.bind()) if not x.startswith("__")]

    @property
    def entitlements(self):
        xml: str = self.session.bind().GetEntitlements()
        return parser.parse(xml)

    def connect(self) -> bool:
        """Initiate a connection to the soap service"""
        return self.service.Login(_soapheaders=self.soapheaders)

    def build(self, params: dict, target: dict) -> str:
        if "Ids" in params.keys():
            return self.service.BuildExport(params, target)
        else:
            return self.service.BuildExportFromQuery(params, target)

    def build_from_query(self, params: dict, target: dict) -> str:
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
        tags: Dict = {}
        if not isinstance(job, ExportJob):
            job = ExportJob(job_id=job)

        tags = job.limited_dict()
        job_id = job.job_id

        try:
            result = self.service.DeleteExport(job_id)
            logger.info("Deleted job: %s", job_id)
            metrics.post("job.delete.success", 1, tags=tags)
        except Exception as e:
            logger.exception(
                "Encountered error when deleting job %s -- %s", job_id, e,
            )
            metrics.post("job.delete.error", 1, tags=tags)

        return result

    def job_exists(self, job: Union[ExportJob, str]) -> bool:
        if isinstance(job, ExportJob):
            job = job.job_id
        return self.service.Exists(job)

    def list_completed_jobs(self) -> List[str]:
        try:
            return self.service.GetCompleteExports() or []
        except ConnectionError as e:
            msg = f"Error connecting to IHS service -- {e}"
            logger.error(msg)
            raise CollectorError(msg) from e
        except (zeep.exceptions.TransportError, ProtocolError) as e:
            msg = f"Bad response from IHS service -- {e}"
            logger.error(msg)
            raise CollectorError(msg) from e

    def delete_all_jobs(self):
        jobs = self.list_completed_jobs()
        deleted = 0
        logger.info(f"Deleting {len(jobs)} exports from remote")
        for job in jobs:
            deleted += 1 if self.delete_job(job) else 0
        logger.warning(f"Deleted {deleted} of {len(jobs)} exports from remote")


class ExportBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="exportbuilder", *args, **kwargs)

    def submit(
        self, export_param: ExportParameter, metadata: dict
    ) -> Union[ExportJob, None]:

        tags = {
            k: v
            for k, v in metadata.items()
            if k in ["endpoint", "task", "hole_direction", "data_type"]
        }

        try:
            job_id = self.build(export_param.params, export_param.target)
            return ExportJob(job_id=job_id, **{**metadata, **dict(export_param)})
        except (ConnectionError, ProtocolError) as e:
            msg = f"Encountered error when connecting to IHS remote service -- {e}"
            # logger.error(msg, extra=metadata)
            logger.error(msg)
            metrics.post("job.submitted.error", 1, tags=tags)

        except Exception as e:
            msg = f"Error getting job id from service for data type {export_param.data_type} -- {e}"

            if "No ids to export" in e.args[0]:
                # logger.info(msg, extra=metadata)
                logger.info(msg)
            else:
                # logger.warning(msg, extra=metadata)
                logger.warning(msg)
                metrics.post("job.submitted.error", 1, tags=tags)

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
        super().__init__(endpoint=None, *args, **kwargs)
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
        self, page: int = None, domain: str = None, data_type: str = "Well",
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

        # "PagingDetails" and "Result" are proerties of the result
        # object defined in the backing WSDL
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

    def get(self, auto_delete: bool = True) -> Union[str, None]:
        result = None

        try:
            result = self.client.service.RetrieveExport(self.job.job_id)
        except Exception as e:
            msg = f"Failed retrieving export {self.job} -- {e}"
            # Suppress errors from empty exports
            if "No ids to export" in e.args[0]:
                logger.debug(msg)
            elif "does not exist" in e.args[0]:
                logger.warning(msg, exc_info=True, stack_info=True)
                metrics.post("job.retrieve.error", 1, tags=["file_does_not_exist"])
            else:
                logger.warning(msg, exc_info=True, stack_info=True)
                metrics.post("job.retrieve.error", 1)

        if result is not None and auto_delete:
            self.client.delete_job(self.job)

        return result


if __name__ == "__main__":

    from config import get_active_config
    from ihs.config import get_active_config
    from ihs import create_app
    from collector import Endpoint
    from util import to_json
    from collector import XMLParser
    import pandas as pd
    import numpy as np

    conf = get_active_config()
    app = create_app()
    app.app_context().push()

    logging.basicConfig(level=20)

    eb = ExportBuilder(None)
    len(eb.list_completed_jobs())

    endpoints = Endpoint.load_from_config(conf, load_disabled=True)
    endpoint = endpoints.get("well_master_horizontal")

    # cde = CDExporter("2018/10/13", "2019/11/04", endpoint=endpoint)
    cde = CDExporter("2020/01/01", "2020/03/31", endpoint=endpoint)
    self = cde
    results = cde.get_all()

    # from collector import Collector

    # records = []
    # max_sequence = ChangeDeleteLog.max_sequence()
    # for r in results:
    #     new = {}
    #     for k, v in r.items():
    #         if v is not None:
    #             if "uwi" in k:
    #                 v = str(v)
    #             new[k] = v
    #     if new.get("sequence", 0) > max_sequence:
    #         records.append(new)

    # collector = Collector(ChangeDeleteLog)
    # collector.save(records)

    # reasons = pd.read_csv(
    #     "/Users/friedrichb/repo/ihs-deo/doc/change_and_delete_reason_codes.csv"
    # ).set_index("reason_code")

    # reasons.reset_index().to_dict(orient="records")

    # import pandas as pd

    # df = pd.DataFrame(records)

    # x = []
    # for uwi in df.uwi.values:
    #     obj = WellHorizontal.objects(api14=uwi).first()
    #     if x:
    #         x.append(obj)

    # dt = datetime.datetime.now() - datetime.timedelta(days=3)
    # WellHorizontal.objects(last_update_at__lte=dt)
