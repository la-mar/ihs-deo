from app.connection import *
from app.util import *
from app.mongo import *


from time import sleep
import xmltodict
import pprint
import json
from lxml import etree

QUERY_DIR = 'queries/'



def import_query(name: str){
    """query name is file name"""

    }

def list_queries(){

}

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

def get_default_params(){
    return {
            'Domain':'US',
            'DataType': 'Well',
            # 'Template': 'EnerdeqML Well',
            'Template': well_template,
            'Query': well_query_driftwood
            }
}

def get_default_target(){
    return {
            'Filename':'Sample',
            'Overwrite': 'True'
            }
}

def is_complete(job_id):
    return exportbuilder.service.IsComplete(job_id, _soapheaders=[header_value])



def driftwood_wells(decode = False):

    job_id = exportbuilder.service.BuildExportFromQuery(get_default_params(), get_default_target(), _soapheaders=[header_value])

    while not is_complete(job_id):
        n = 5
        print(f'Sleeping for {n} secs')
        sleep(n)

    data = exportbuilder.service.RetrieveExport(job_id, _soapheaders=[header_value])

    if decode:
        return data.decode('utf-8')
    else:
        return data

def get_wells(decode = False):

    job_id = exportbuilder.service.BuildExportFromQuery(get_default_params(), get_default_target(), _soapheaders=[header_value])

    while not is_complete(job_id):
        n = 5
        print(f'Sleeping for {n} secs')
        sleep(n)

    data = exportbuilder.service.RetrieveExport(job_id, _soapheaders=[header_value])

    if decode:
        return data.decode('utf-8')
    else:
        return data


def elevate_api(wellbore: dict) -> dict:
    """ Moves a well's identification number (api) to the top level of
        the dictionary."""

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

    return wellbore


if __name__ == "__main__":

    """wells_xml = driftwood_wells()

    wells_json = json.dumps(xmltodict.parse(wells_xml), indent = 4)
    to_file(wells_json, 'wells_json.json')
    """

    def download_well_headers():
        """ one or many"""


    # from lxml import objectify
    wells_bin = driftwood_wells(decode = False)
    xml = objectify.fromstring(wells_bin)
    root = xml.getroottree().getroot()
    wellbores = [child for child in root.getchildren() if child.tag == 'WELLBORE']
    c = wellbores[0]
    # wellbores = xmltodict.parse(c)

    #convert child into dictionary
    xmltojson = etree.tostring(c)
    wellbore = xmltodict.parse(xmltojson)['WELLBORE']



    to_file(json.dumps(wellbore, indent = 4), 'wellbore.json')
    # write to mongodb
    db.wells.insert(wellbore)

    x = db.wells.find_one({'api14': '42383374130000'})






