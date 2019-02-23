from app.connection import *
from time import sleep

well_query_driftwood = """<criterias>
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
#14207C0183842
#42461343350001

params = {
'Domain':'US',
'DataType': 'Well',
'Template': 'EnerdeqML Well',
'Query': well_query_driftwood
}

target = {
  'Filename':'Sample',
'Overwrite': 'True'
}

def is_complete(job_id):
    return EB.service.IsComplete(job_id, _soapheaders=[header_value])

def driftwood_wells():

    job_id = EB.service.BuildExportFromQuery(params, target, _soapheaders=[header_value])

    while not is_complete(job_id):
        n = 5
        print(f'Sleeping for {n} secs')
        sleep(n)

    data = EB.service.RetrieveExport(job_id, _soapheaders=[header_value])

    return data.decode('utf-8')



