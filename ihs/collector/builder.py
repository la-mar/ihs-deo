from __future__ import annotations
import logging

from typing import Union
from collector.soap_requestor import SoapRequestor
from collector.export_parameter import ExportParameter

logger = logging.getLogger(__name__)


class ExportJob:
    def __init__(self, job_id: str, **kwargs):
        self.job_id = job_id
        self.attrs = kwargs

    def __repr__(self):
        return f"ExportJob: {self.job_id}"

    def to_dict(self):
        return {"job_id": self.job_id, **self.attrs}


class Builder(SoapRequestor):
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
