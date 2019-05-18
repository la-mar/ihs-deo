from app.connection import *
from app.util import *
from app.mongo import *


from time import sleep
import xmltodict
import pprint
import json

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

well_template = """
    <EXPORT>
        <TEXTUAL_EXPORTS>
            <WELL_XML INCLUDE_PRODFIT='TRUE'>
            </WELL_XML>
        </TEXTUAL_EXPORTS>
    </EXPORT>"""

params = {
    'Domain':'US',
    'DataType': 'Well',
    # 'Template': 'EnerdeqML Well',
    'Template': well_template,
    'Query': well_query_driftwood
    }

target = {
  'Filename':'Sample',
  'Overwrite': 'True'
    }

def is_complete(job_id):
    return EB.service.IsComplete(job_id, _soapheaders=[header_value])

def driftwood_wells(decode = True):

    job_id = EB.service.BuildExportFromQuery(params, target, _soapheaders=[header_value])

    while not is_complete(job_id):
        n = 5
        print(f'Sleeping for {n} secs')
        sleep(n)

    data = EB.service.RetrieveExport(job_id, _soapheaders=[header_value])

    if decode:
        return data.decode('utf-8')
    else:
        return data


if __name__ == "__main__":

    """wells_xml = driftwood_wells()

    wells_json = json.dumps(xmltodict.parse(wells_xml), indent = 4)
    to_file(wells_json, 'wells_json.json')
    """


    # from lxml import objectify
    wells_bin = driftwood_wells(decode = False)
    xml = objectify.fromstring(wells_bin)
    root = xml.getroottree().getroot()
    children = [child for child in root.getchildren() if child.tag == 'WELLBORE']
    c = children[0]
    # wellbores = xmltodict.parse(c)

    #convert child into dictionary
    from lxml import etree
    xmltojson = etree.tostring(c)
    wellbore = xmltodict.parse(xmltojson)['WELLBORE']
    api = wellbore['METADATA']['IDENTIFICATION']

    if len(api) == 14:
        wellbore['api14'] = api
        wellbore['api10'] = api[:10]
    elif len(api) == 10:
        wellbore['api10'] = api
        wellbore['api14'] = api + '0000'

    #move new elements to beginning of ordered dict
    wellbore.move_to_end('api14', last=False)
    wellbore.move_to_end('api10', last=False)

    # for key, value in ids.items():
    #     wellbore.update({x['@TYPE']: x['#text']})
    #     wellbore.move_to_end(x['@TYPE'], last=False)


    to_file(json.dumps(wellbore, indent = 4), 'wellbore.json')
    # write to mongodb
    db.wells.insert_many(wellbore)








