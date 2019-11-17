from __future__ import annotations
import logging

from typing import Union
from collector.soap_requestor import SoapRequestor
from collector.export_parameter import ExportParameter
from config import get_active_config

conf = get_active_config()

logger = logging.getLogger(__name__)


class ExportJob:
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


class ExportBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="exportbuilder", *args, **kwargs)

    def submit(self, export_param: ExportParameter) -> Union[ExportJob, None]:

        try:
            job_id = self.build(export_param.params, export_param.target)
            return ExportJob(job_id)
        except Exception as e:
            logger.error(
                f"Error getting job id from service for data type {export_param.data_type} {e}"
            )
        return None


class QueryBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="querybuilder", *args, **kwargs)


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
            return self.client.service.RetrieveExport(self.job.job_id)
        except Exception as e:
            logger.exception(f"Failed retrieving export {self.job} -- {e}")

        return None
