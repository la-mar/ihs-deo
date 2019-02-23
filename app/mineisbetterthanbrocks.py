


import zeep
wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\Session.wsdl'
qb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\QueryBuilder.wsdl'
eb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\ExportBuilder.wsdl'

client = zeep.Client(wsdl=wsdl)


def get_count():
  print(qb_client.service.GetCount(qb_query, "Well", "US", _soapheaders=[header_value]))

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

client.service.Login(_soapheaders=[header_value])

# qb_client = zeep.Client(wsdl = qb_wsdl)

# qb_query = """<criterias>
#     <criteria type="group" groupId="" ignored="false">
#         <domain>US</domain>
#         <datatype>Well</datatype>
#         <attribute_group>Identification</attribute_group>
#         <attribute>Current Operator</attribute>
#         <filter logic="include">
#             <value id="0" ignored="false">
#                 <group_actual>
#                     <operator logic="and">
#                         <condition logic="equals">
#                             <attribute>code</attribute>
#                             <value_list>
#                                 <value>278107</value>
#                             </value_list>
#                         </condition>
#                     </operator>
#                 </group_actual>
#                 <group_display>name = DRIFTWOOD ENERGY OPERATING LLC</group_display>
#             </value>
#         </filter>
#     </criteria>
# </criterias>"""

#print(qb_client.service.GetCount(qb_query, "Well", "US", _soapheaders=[header_value]))

eb_client = zeep.Client(eb_wsdl)

params = {
'Domain':'US',
'DataType': 'Well',
'Template': 'EnerdeqML Well',
'Ids': ["42383402790000"]
}

target = {
  'Filename':'Sample',
'Overwrite': 'False'
}

job_id = eb_client.service.BuildExport(params, target, _soapheaders=[header_value])