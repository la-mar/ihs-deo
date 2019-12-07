from collector.yammler import Yammler
from config import get_active_config
from typing import Dict, List, Union, no_type_check
import logging
import json
import xml.etree.ElementTree as ET
import pprint

conf = get_active_config()
logger = logging.getLogger(__name__)

collector_yaml = conf.COLLECTOR_CONFIG_PATH
criteria_hole_direction = """
<criteria type="group" groupId="" ignored="false">
        <domain>US</domain>
        <datatype>{data_type}</datatype>
        <attribute_group>Well</attribute_group>
        <attribute>Hole Direction</attribute>
        <filter logic="include">
            <value id="0" ignored="false">
                <group_actual>
                    <operator logic="and">
                        <condition logic="equals">
                            <attribute>code</attribute>
                            <value_list>
                                <value>{value}</value>
                            </value_list>
                        </condition>
                    </operator>
                </group_actual>
                <group_display>name = HORIZONTAL</group_display>
            </value>
        </filter>
    </criteria>
    """
# mappings for yaml
data_type_map = "/options/data_type"
criteria_map = "/options/criteria"


class XmlSchemaBuilder:
    def __init__(
        self, cache: str = None, **kwargs,
    ):
        self.cache = Yammler(cache or collector_yaml)

    def get_criterias(self) -> Union[dict, None]:
        if not self.cache:
            logger.info("Yaml file not found when building xml schema")
            return None

        criterias = {}

        if "endpoints" in self.cache:
            endpoints = self.cache["endpoints"]
            endpoint_keys = endpoints.keys()
            for key in endpoint_keys:
                record = {key: endpoints[key] for key in endpoints.keys() & {key}}
                dict_test = QueryableDictionary(record)
                data_type = dict_test.get(f"{key}{data_type_map}")
                criteria = dict_test.get(f"{key}{criteria_map}")
                for k, v in criteria.items():
                    if k == "hole_direction":
                        criterias[key] = criteria_hole_direction.format(
                            data_type=data_type, value=v
                        )
        else:
            logger.info("Criterias do not exist in yaml file")

        return criterias


class QueryableDictionary(dict):
    def get(self, path, default=None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break

        return val


if __name__ == "__main__":

    pp = pprint.PrettyPrinter(indent=3)

    endpoints = conf.endpoints

    # builder = XmlSchemaBuilder(collector_yaml)
    # d = builder.get_criterias()
    # pp.pprint(d)
    # keyword = "well_horizontal"
    # endpoints = builder.cache["endpoints"]

    # for k, v in test.cache["endpoints"].items():
    #     if k == endpoint:
    #         json.dumps(v, indent=4)

    # endpoint_keys = endpoints.keys()
    # for key in endpoint_keys:
    #     record = {key: endpoints[key] for key in endpoints.keys() & {key}}
    #     dict_test = QueryableDictionary(record)
    #     data_type = dict_test.get(f"{key}/options/data_type")
    #     criteria = dict_test.get(f"{key}/options/criteria")
    #     for k, v in criteria.items():
    #         if k == "hole_direction":
    #             criterias[key] = criteria_hole_direction.format(
    #                 data_type=data_type, value=v
    #             )
    #     pp.pprint(criterias)
    # res = {key: values[key] for key in values.keys() & {"options"}}

