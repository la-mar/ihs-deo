import functools
import logging
import os
import pprint
from typing import Dict, List, Union, no_type_check

import util
from collector.yammler import Yammler
from config import get_active_config
from util import query_dict

conf = get_active_config()
logger = logging.getLogger(__name__)

criteria_hole_direction = "criteria_hole_direction.xml"  # move to config
criteria_operator = "criteria_operator.xml"  # move to config
# mappings for yaml
data_type_map = "options.data_type"  # move to config
criteria_map = "options.criteria"  # move to config
query_basepath = conf.QUERY_PATH


class XmlSchemaBuilder:
    def get_criteria(self, endpoint_name: str = None) -> Union[dict, None]:
        criterias = {}
        endpoints = conf.endpoints
        if any(endpoints):
            try:
                record = endpoints[endpoint_name]
                get = functools.partial(query_dict, data=record)
                data_type = get(data_type_map)
                criteria = get(criteria_map)
                print(len(criteria.items()))
                for k, v in criteria.items():
                    if k == "hole_direction":
                        query = self.load_query(
                            criteria_hole_direction, data_type=data_type, value=v
                        )
                        criterias[endpoint_name] = query
                    if k == "operator":
                        query = self.load_query(
                            criteria_operator,
                            data_type=data_type,
                            value=v,
                            name="DRIFTWOOD ENERGY OPERATING LLC",  # not sure yet where to dynamically get this. Add new item in yaml?
                        )
                        criterias[endpoint_name] = query
            except Exception as e:
                logger.error(
                    "Encountered error when building criteria xml for endpoint %s -- %s",
                    endpoint_name,
                    e,
                )
                return None
        else:
            logger.error("Endpoints do not exist in yaml file")
            return None

        return criterias

    def finalize_criteria_xml(self, criterias: dict) -> str:
        st_builder = "<criterias>\n"

        for v in criterias.values():
            st_builder += v

        st_builder += "\n</criterias>"

        return st_builder

    # move this to utility class that anything can access
    def load_query(self, path: Union[str, None], **kwargs) -> Union[str, None]:
        if path:
            if not os.path.exists(path):
                path = os.path.join(query_basepath, path)

            try:
                return util.load_xml(path).format(**kwargs)
            except FileNotFoundError as fe:
                logger.error("Failed to load xml file %s -- %s", path, fe)
                raise
        else:
            return None


if __name__ == "__main__":

    pp = pprint.PrettyPrinter(indent=3)
    builder = XmlSchemaBuilder()
    d = builder.get_criteria("well_master_horizontal")
    final = builder.finalize_criteria_xml(d)
    pp.pprint(final)
