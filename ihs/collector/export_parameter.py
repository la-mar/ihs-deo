from typing import Union
import logging
import os

from uuid import uuid4
from config import get_active_config
import util


logger = logging.getLogger(__name__)
conf = get_active_config()


class ExportParameter:
    """ Next step move this to be config driven """

    domain = conf.API_DOMAIN
    query_basepath = conf.QUERY_PATH

    def __init__(
        self,
        data_type: str,
        template: str = None,
        query: str = None,
        template_path: str = None,
        query_path: str = None,
        overwrite: bool = True,
        domain: str = None,
        **kwargs,
    ):

        self._export_filename = uuid4()
        self.data_type = data_type
        self.query = (
            query or self.load_query(query_path, **kwargs, data_type=data_type) or None
        )
        self.template = (
            template
            or self.load_query(template_path, **kwargs, data_type=data_type)
            or None
        )
        self.overwrite = overwrite
        self.domain = domain or self.domain

    def __repr__(self):
        return (
            f"ExportParameter: {self.domain}/{self.data_type} - {self.export_filename}"
        )

    def __iter__(self):
        for key, value in self.to_dict().items():
            yield key, value

    def to_dict(self):
        return {
            "domain": self.domain,
            "data_type": self.data_type,
            "template": self.template,
            "query": self.query,
            "overwrite": self.overwrite,
            "export_filename": self.export_filename,
        }

    @property
    def export_filename(self):
        return self._export_filename

    @property
    def params(self) -> dict:
        return {
            "Domain": self.domain,
            "DataType": self.data_type,
            "Template": self.template,
            "Query": self.query,
        }

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value: str):
        """ query can be either the name of a query saved in IHS or an XML string of criteria """
        self._query = value

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value: str):
        """ template can be either the name of a template saved in IHS or an XML string of criteria """
        self._template = value

    @classmethod
    def load_query(cls, path: Union[str, None], **kwargs) -> Union[str, None]:
        if path:
            if not os.path.exists(path):
                path = os.path.join(cls.query_basepath, path)

            try:
                return util.load_xml(path).format(**kwargs)
            except FileNotFoundError as fe:
                logger.warning("Failed to load xml file %s -- %s", path, fe)
                raise
        else:
            return None

    @property
    def target(self) -> dict:
        return {"Filename": self.export_filename, "Overwrite": self.overwrite}


if __name__ == "__main__":

    from ihs import create_app, db
    from collector.endpoint import Endpoint

    app = create_app()
    app.app_context().push()

    conf = get_active_config()
    endpoints = Endpoint.load_from_config(conf)
    endpoint = endpoints["well_horizontal"]

    task = endpoint.tasks["sync"]

    # print(task.options)
    ep = ExportParameter(**task.options.to_list()[0])
    # ep = ExportParameter(
    #     data_type="Well",
    #     query_path="well_horizontal_by_county",
    #     template="EnerdeqML Well",
    #     name="tx-upton",
    #     state_code=42,
    #     county_code=461,
    # )

    ep.query = None
    print(dict(ep))

