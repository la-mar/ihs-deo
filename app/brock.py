


import zeep
wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\Session.wsdl'
qb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\QueryBuilder.wsdl'
eb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\ExportBuilder.wsdl'

CC = zeep.Client(wsdl=wsdl)
QB = zeep.Client(wsdl=qb_wsdl)
EB = zeep.Client(wsdl=eb_wsdl)
# client = zeep.Client(wsdl=wsdl)

API = "42383402790000"

domain = 'US'

dtypes = ['Well', 'Production Allocated']

def methods(obj) -> None:
    return [x for x in dir(obj) if not x.startswith('__')]

def m(obj):
    return methods(obj)

def get_count():
    'Put query that worked here'

from zeep import xsd

user = 'brock@driftwoodenergy.com'
password = 'YrUs0LAME!'
appName = 'driftwood_wellprod_digest'

header = xsd.Element(
    '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Header',
    xsd.ComplexType([
        xsd.Element(
            '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Username',
            xsd.String()),
            xsd.Element(
            '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Password',
            xsd.String()),
            xsd.Element(
            '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Application',
            xsd.String())
    ])
)

header_value = header(Username=user, Password = password, Application = appName)

_soapheaders = [header_value]

CC.service.Login(_soapheaders = _soapheaders)

CC.service.GetEntitlements(_soapheaders = _soapheaders) # works

s = EB.service

EB.service.GetExportTemplates(domain, 'Well', _soapheaders)

wellquery = """
<criterias>
  <criteria type="value">
    <domain>US</domain>
    <datatype>Production Allocated</datatype>
    <attribute_group>Location</attribute_group>
    <attribute>Basin</attribute>
    <type>name</type>
    <filter logic="equals">
      <value  actual="PERMIAN BASIN"/>
    </filter>
  </criteria>
</criterias>
"""



s = QB.service

s.GetCount(wellquery, 'Well', 'US', _soapheaders = _soapheaders)

s.ValidateIds(domain, "Well", "UWI", Ids = ["42383402790000"], _soapheaders = _soapheaders)

lookup_parameters = {
    'Domain': 'US',
    'DataType': 'Well',
    'Attr': 'Current Operator',#'API/IC Number',
    'SearchValue': 'Driftwood',
    'Operator': 'StartsWith'
}

x = s.LookupName(lookup_parameters, _soapheaders = _soapheaders)


def lookup_name() -> list:
    """Example output:
        ['DRIFTWOOD ENERGY OPERATING LLC',
        'DRIFTWOOD GERMANIA',
        'DRIFTWOOD OIL COMPANY',
        'DRIFTWOOD OIL LLC',
        'DRIFTWOOD OPERATING COMPANY',
        'DRIFTWOOD STORAGE LLC']
    """
    lookup_parameters = {
        'Domain': 'US',
        'DataType': 'Well',
        'Attr': 'Current Operator',
        'SearchValue': 'Driftwood',
        'Operator': 'StartsWith'
    }
    return QB.service.LookupName(lookup_parameters, _soapheaders = _soapheaders)



lookup_parameters = {
    'Domain': 'US',
    'DataType': 'Well',
    'IDs': ['42461343350001'],
    'Attrs': 'Operator Name',
    'StartDate': '2018/10/01',
    'EndDate': '2019/10/01',
    # 'SearchValue': 'Driftwood',
    # 'Operator': 'StartsWith'

}

# ns2: GetProductionEntityAttributesParameters(Domain: xsd: string, DataType: xsd: string, IDs: ns1: ArrayOfId, Attrs: ns1: ArrayOfStrings, StartDate: xsd: string, EndDate: xsd: string)

wellquery2 = """
<criterias>
    <criteria type="group" groupId="" ignored="false">
        <domain>US</domain>
        <datatype>Production Allocated</datatype>
        <attribute_group>Identification</attribute_group>
        <attribute>Operator</attribute>
        <filter logic="include">
            <value id="0" ignored="false">
                <group_actual>
                    <operator logic="and">
                        <condition logic="equals">
                            <attribute>code</attribute>
                            <value_list>
                                <value>278107</value>
                            </value_list>
                        </condition>
                    </operator>
                </group_actual>
                <group_display>name = DRIFTWOOD ENERGY OPERATING LLC</group_display>
            </value>
        </filter>
    </criteria>
</criterias>
"""

xml = QB.service.GetAttributes(wellquery2, _soapheaders = _soapheaders)

import pandas as pd

from lxml import objectify
xml = objectify.fromstring(xml)
root = xml.getroottree().getroot()

records = [child.text for child in root['record-meta'].getchildren()]

df = xml_dataframe