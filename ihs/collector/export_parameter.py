import logging

from uuid import uuid4
from config import get_active_config
import util


logger = logging.getLogger(__name__)
conf = get_active_config()


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


if __name__ == "__main__":

    from ihs import create_app, db
    from collector.endpoint import load_from_config

    app = create_app()
    app.app_context().push()

    config = get_active_config()
    endpoints = load_from_config(config)
    endpoint = endpoints["wells"]

    task = endpoint.tasks["sync"]

    ep = ExportParameter(**task.options)

    ep.params
    ep.target
