from collector.soap_requestor import SoapRequestor


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

    def submit_job(self, export_param: ExportParameter) -> Union[str, None]:

        try:
            return self.build(export_param.params, export_param.target)
        except Exception as e:
            print(
                f"Error getting job id from service for data type {export_param.data_type} {e}"
            )

    # def job_is_complete(self, job_id: str) -> bool:
    #     try:
    #         if self.client.service.IsComplete(job_id):
    #             return True
    #         return False
    #     except Exception as e:
    #         print(f"Could not determine state of Job Id {job_id} {e}")
    #         return False

    # def get_data(self, job_id: str) -> Union[str, None]:

    #     try:
    #         return self.client.service.RetrieveExport(job_id)
    #     except Exception as e:
    #         print(e)


class QueryBuilder(Builder):
    def __init__(self, *args, **kwargs):
        super().__init__(client_type="querybuilder", *args, **kwargs)
