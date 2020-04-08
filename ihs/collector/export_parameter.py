import logging
import os
from typing import Union, List
from uuid import uuid4

import util
from config import get_active_config
from collector.xml_query import XMLQuery
import xmltodict
from exc import NoIdsError

logger = logging.getLogger(__name__)
conf = get_active_config()


class ExportParameter:

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
        values: List[str] = None,
        **kwargs,
    ):

        self._export_filename = uuid4()
        self.data_type = data_type
        self.values = values
        self.query = self._set_query(
            xml=query, filepath=query_path, values=values, **kwargs
        )
        # self.query = (
        #     query or self.load_query(query_path, **kwargs, data_type=data_type) or None
        # )
        self.template = (
            template
            or self.load_query(template_path, **kwargs, data_type=data_type)
            or None
        )  # TODO: use only Enum
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
            # "ids": self.values,
            "overwrite": self.overwrite,
            "export_filename": self.export_filename,
        }

    def _set_query(
        self, xml: str = None, filepath: str = None, values: List[str] = None, **kwargs
    ) -> str:
        query = None
        value_kwargs = {}

        if xml:
            query = xml
        elif filepath:
            # inject dynamic value_list
            try:
                if values:
                    value_kwargs["value_list"] = xmltodict.unparse(
                        {"value_list": {"value": values}},
                        pretty=False,
                        full_document=False,
                    )
                query = self.load_query(
                    filepath, **kwargs, data_type=self.data_type, **value_kwargs
                )
            except KeyError as ke:
                if ke.args[0] == "value_list":
                    raise NoIdsError("No ids to export") from ke
                else:
                    logger.debug(f"Missing parameters in query formatter: {ke.args}")

        elif values:
            if values:
                query = (
                    XMLQuery(data_type=self.data_type, domain=self.domain,).add_filter(
                        values
                    )
                    # .to_xml()
                )
            else:
                logger.info(f"No values found when generating query")

        if not query:
            raise ValueError(
                f"Unable to determine query from parameters: xml={xml} filepath={filepath} values={values}"  # noqa
            )
        return query

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
            # "Ids": self.values,
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
        """ template can be either the name of a template saved in IHS
        or an XML string of criteria """
        self._template = value

    @classmethod
    def load_query(cls, path: Union[str, None], **kwargs) -> Union[str, None]:
        if path:
            if not os.path.exists(path):
                path = os.path.join(cls.query_basepath, path)

            try:
                return util.load_xml(path).format(**kwargs)
            except KeyError:
                raise
            except FileNotFoundError as fe:
                logger.error(f"Failed to load xml file {path} -- {fe}")
                raise
        else:
            return None

    @property
    def target(self) -> dict:
        return {"Filename": self.export_filename, "Overwrite": self.overwrite}


if __name__ == "__main__":

    raw_query = """
                <criterias>
                    <criteria type="lists" ignored="False">
                            <domain>US</domain>
                            <datatype>Well</datatype>
                            <listtype>API/IC Number</listtype>
                            <filter logic="include">
                                    <value id="0" ignored="false">
                                            <keys>
                                                    <key>42413001340100</key>
                                                    <key>42413329660000</key>
                                                    <key>42413005390100</key>
                                            </keys>
                                    </value>
                            </filter>
                    </criteria>
            </criterias>
            """

    ep = ExportParameter("Well", query=raw_query)
    print(ep.query)

    ep = ExportParameter(
        "Well", values=["42413001340100", "42413329660000", "42413005390100"]
    )
    print(ep.query)

    ep = ExportParameter(
        "Well",
        query_path="well_by_api.xml",
        values=["42413001340100", "42413329660000", "42413005390100"],
    )
    print(ep.query)

    ep = ExportParameter(
        "Production",
        query_path="production_by_api.xml",
        values=["42413001340100", "42413329660000", "42413005390100"],
    )
    print(ep.query)

    ep = ExportParameter("Production", query_path="production_by_api.xml", values=[],)
    print(ep.query)
