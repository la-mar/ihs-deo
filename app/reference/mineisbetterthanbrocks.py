


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

well_query = """<criterias>
    <criteria type="group" groupId="" ignored="false">
        <domain>US</domain>
        <datatype>Well</datatype>
        <attribute_group>Identification</attribute_group>
        <attribute>Current Operator</attribute>
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
</criterias>"""

#print(qb_client.service.GetCount(qb_query, "Well", "US", _soapheaders=[header_value]))

eb_client = zeep.Client(eb_wsdl)
#14207C0183842
#42461343350001

well_template = """
<EXPORT>
    <TEXTUAL_EXPORTS>
        <WELL_XML EXCLUDE_MISSING_LATLONGS="TRUE" INCLUDE_PRODFIT="TRUE" INCLUDE_SUBSCRIBED_LATLONG_SOURCES="TRUE">
            <BRANCH NAME="/WELL_SET/WELLBORE/TESTS" />
        </WELL_XML>
    </TEXTUAL_EXPORTS>
</EXPORT>"""


params_well = {
'Domain':'US',
'DataType': 'Well',
'Template': well_template,
'Query': well_query
}

target = {
  'Filename':'Sample',
'Overwrite': 'True'
}

job_id = eb_client.service.BuildExportFromQuery(params_well, target, _soapheaders=[header_value])

data = eb_client.service.RetrieveExport(job_id, _soapheaders=[header_value])

with open("sample.xml", "w") as f :
  f.writelines(data.decode("utf-8"))

prod_query = """
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
params_prod = {
'Domain':'US',
'DataType': 'Production Allocated',
'Template': 'EnerdeqML Production',
'Query': prod_query
}

target = {
  'Filename':'Sample',
'Overwrite': 'True'
}

prod_job_id = eb_client.service.BuildExportFromQuery(params_prod, target, _soapheaders=[header_value])

data = eb_client.service.RetrieveExport(job_id, _soapheaders=[header_value])

data = data.decode('utf-8')



prod_data = eb_client.service.RetrieveExport(prod_job_id, _soapheaders=[header_value])
