
from app.connection import *
from time import sleep

eb_client = zeep.Client(esdl_exportbuilder)

# Braches can limit what sections of the data we pull
prod_template = """
<EXPORT>
    <TEXTUAL_EXPORTS>
        <PRODUCTION_XML>
            <BRANCH NAME="/PRODUCTION_SET/PRODUCING_ENTITY/PRODUCTION"/>
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
            <value id="1" ignored="false" actual="2013/2/1 00:00:00--2019/2/23 23:59:59.999999999" />
        </filter>
    </criteria>
    <criteria type="value" ignored="false">
        <domain>US</domain>
        <datatype>Production Allocated</datatype>
        <attribute_group>Date</attribute_group>
        <attribute>Production Start Date</attribute>
        <type>date</type>
        <displaytype />
        <filter logic="between">
            <value id="2" ignored="false" actual="2012/1/1 00:00:00--2019/2/23 23:59:59.999999999" />
        </filter>
    </criteria>
    <criteria type="value" ignored="false">
        <domain>US</domain>
        <datatype>Production Allocated</datatype>
        <attribute_group>Date</attribute_group>
        <attribute>Production Stop Date</attribute>
        <type>date</type>
        <displaytype />
        <filter logic="between">
            <value id="2" ignored="false" actual="2018/2/1 00:00:00--2019/2/28 23:59:59.999999999" display="between 2/1/2018 and 2/28/2019" />
        </filter>
    </criteria>
</criterias>
"""
params_prod = {
'Domain':'US',
'DataType': 'Production Allocated',
#'Template': prod_template,
'Template': 'EnerdeqML Production',
'Query': prod_query
}

target = {
  'Filename':'Sample',
'Overwrite': 'True'
}

def is_complete(job_id):
    return exportbuilder.service.IsComplete(job_id, _soapheaders=[header_value])

prod_job_id = eb_client.service.BuildExportFromQuery(params_prod, target, _soapheaders=[header_value])

while not is_complete(prod_job_id):
        n = 5
        print(f'Sleeping for {n} secs')
        sleep(n)

prod_data = eb_client.service.RetrieveExport(prod_job_id, _soapheaders=[header_value])

