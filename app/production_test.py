import zeep
wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\Session.wsdl'
qb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\QueryBuilder.wsdl'
eb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\ExportBuilder.wsdl'

client = zeep.Client(wsdl=wsdl)

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

eb_client = zeep.Client(eb_wsdl)


prod_template = """
<EXPORT>
    <TEXTUAL_EXPORTS>
        <PRODUCTION_XML>
            <BRANCH NAME="/PRODUCTION_SET/PRODUCING_ENTITY/PRODUCTION " />
        </PRODUCTION_XML>
    </TEXTUAL_EXPORTS>
</EXPORT>"""

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
    <criteria type="value" ignored="false">
        <domain>US</domain>
        <datatype>Production Allocated</datatype>
        <attribute_group>Date</attribute_group>
        <attribute>Last Update</attribute>
        <type>date</type>
        <displaytype />
        <filter logic="between">
            <value id="0" ignored="false" display="between 2/1/2019 and 2/23/2019" actual="2019/2/1 00:00:00--2019/2/23 23:59:59.999999999" />
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

prod_data = eb_client.service.RetrieveExport(prod_job_id, _soapheaders=[header_value])

with open("sample_prod_2011_10.xml", "w") as f :
  f.writelines(prod_data.decode("utf-8"))