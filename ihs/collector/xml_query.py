from typing import List, Union, Dict
import xmltodict
from config import ExportDataTypes, NamedTemplates, get_active_config

conf = get_active_config()

# TODO: Add ability to query by operator
# TODO: Add ability to query by county


class XMLQuery:
    domain: str = conf.API_DOMAIN

    def __init__(
        self,
        data_type: Union[ExportDataTypes, str],
        list_type: str = None,
        domain: str = "US",
        criteria_type: str = "group",
        ignored: bool = False,
    ):
        self.data_type: ExportDataTypes = ExportDataTypes(data_type)
        self.list_type: str = list_type or self._infer_list_type(self.data_type)
        self.domain: str = domain
        self.criteria_type: str = criteria_type
        self.ignored: bool = ignored
        self.filters: List[Dict] = []

    def __str__(self) -> str:
        return self.to_xml(pretty=False)

    def _infer_list_type(self, data_type: ExportDataTypes) -> str:
        if data_type == ExportDataTypes.WELL:
            list_type = "API/IC Number"
        elif data_type == ExportDataTypes.PRODUCTION:
            list_type = "Production ID"
        else:
            raise ValueError(
                f"Cant infer list_type from the provided data_type: {data_type} ({type(data_type).__name__})"  # noqa
            )
        return list_type

    def next_filter_id(self):
        return len(self.filters) + 1

    def add_filter(
        self,
        values: List[str],
        ignored: bool = False,
        filter_id: Union[int, str] = None,
    ):
        filter_id = filter_id or self.next_filter_id()

        self.filters.append(
            {
                "@logic": "include",
                "value": {
                    "@id": 0,
                    "@ignored": "false",
                    "value_list": {"value": values},
                },
            }
        )
        return self

    def to_dict(self) -> Dict:
        return {
            "criterias": {
                "criteria": {
                    "@type": self.criteria_type,
                    "@ignored": self.ignored,
                    "domain": self.domain,
                    "datatype": self.data_type.value,
                    "listtype": self.list_type,
                    "filter": self.filters,
                }
            }
        }

    def to_xml(self, pretty: bool = True) -> str:
        return xmltodict.unparse(self.to_dict(), pretty=pretty, full_document=False)


if __name__ == "__main__":
    api14s = [
        "42461409160000",
        "42383406370000",
        "42461412100000",
        "42461412090000",
        "42461411750000",
        "42461411740000",
        "42461411730000",
        "42461411720000",
        "42461411600000",
        "42461411280000",
        "42461411270000",
        "42461411260000",
        "42383406650000",
        "42383406640000",
        "42383406400000",
        "42383406390000",
        "42383406380000",
        "42461412110000",
        "42383402790000",
        "42461397940000",
    ]
    q = XMLQuery(data_type="Well")
    q.add_filter(api14s)
    q.to_dict()
    print(q.to_xml())
    str(q)

    """
    <criterias>
        <criteria type="lists" ignored="false">
            <domain>US</domain>
            <datatype>Well</datatype>
            <listtype>API/IC Number</listtype>
            <filter logic="include">
                <value id="0" ignored="false">
                    <keys>
                        <key>42383406640000</key>
                        <key>42383406390000</key>
                        <key>42461411750000</key>
                        <key>42461411600000</key>
                        <key>42461409160000</key>
                        <key>42461411280000</key>
                        <key>42461397940000</key>
                        <key>42383406380000</key>
                        <key>42461411740000</key>
                        <key>42383406400000</key>
                        <key>42383406370000</key>
                        <key>42461412100000</key>
                        <key>42461411730000</key>
                        <key>42461411720000</key>
                        <key>42383402790000</key>
                        <key>42383406650000</key>
                        <key>42461411260000</key>
                        <key>42461412110000</key>
                        <key>42461412090000</key>
                        <key>42461411270000</key>
                    </keys>
                </value>
            </filter>
        </criteria>
    </criterias>

    """

    """
    <criterias>
        <criteria type="lists" ignored="false">
            <domain>US</domain>
            <datatype>Production Allocated</datatype>
            <listtype>Production ID</listtype>
            <filter logic="include">
                <value id="0" ignored="false">
                    <keys>
                        <key>14207C0155258418H</key>
                        <key>14207C0155111H</key>
                    </keys>
                </value>
            </filter>
        </criteria>
    </criterias>
    """
