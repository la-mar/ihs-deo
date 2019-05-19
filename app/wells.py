from app.collector import Collector
from app.util import *
from app.mongo import *


from time import sleep
import xmltodict
import pprint
import json
from lxml import etree, objectify
import copy

QUERY_DIR = 'queries/'



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

def get_default_params():
    return {
            'Domain':'US',
            'DataType': 'Well',
            # 'Template': 'EnerdeqML Well',
            'Template': well_template,
            'Query': well_query_driftwood
            }

def get_default_target():
    return {
            'Filename':'Sample',
            'Overwrite': 'True'
            }

# def is_complete(job_id):
#     return exportbuilder.service.IsComplete(job_id, _soapheaders=[header_value])

# def driftwood_wells(decode = False):

#     job_id = exportbuilder.service.BuildExportFromQuery(get_default_params(), get_default_target(), _soapheaders=[header_value])

#     while not is_complete(job_id):
#         n = 5
#         print(f'Sleeping for {n} secs')
#         sleep(n)

#     data = exportbuilder.service.RetrieveExport(job_id, _soapheaders=[header_value])

#     if decode:
#         return data.decode('utf-8')
#     else:
#         return data

# def get_wells(decode = False):

#     job_id = exportbuilder.service.BuildExportFromQuery(get_default_params(), get_default_target(), _soapheaders=[header_value])

#     while not is_complete(job_id):
#         n = 5
#         print(f'Sleeping for {n} secs')
#         sleep(n)

#     data = exportbuilder.service.RetrieveExport(job_id, _soapheaders=[header_value])

#     if decode:
#         return data.decode('utf-8')
#     else:
#         return data

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

def tolower(d: dict):
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key.lower()] = tolower(value)
        elif isinstance(value, list):
            result[key.lower()] = [tolower(x) for x in value]
        else:
            result[key.lower()] = value
    return result

def make_hash(o):

    if isinstance(o, (set, tuple, list)):
        return tuple([make_hash(e) for e in o])

    elif not isinstance(o, dict):
        return hash(o)

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)

    return hash(tuple(frozenset(sorted(new_o.items()))))

def get_apis(encoded_xml):
    xml = objectify.fromstring(encoded_xml)
    root = xml.getroottree().getroot()
    wellbores = [child for child in root.getchildren() if child.tag == 'WELLBORE']

    wellbores_to_update = []
    # iterate through wellbore objects
    number_of_wellbores = len(wellbores)
    for i in range(number_of_wellbores):
        # convert child into dictionary
        xmltojson = etree.tostring(wellbores[i])
        wellbore = xmltodict.parse(xmltojson)['WELLBORE']
        # format json object
        lower_wellbore = tolower(elevate_api(wellbore))
        # create hash of formatted json object
        hashvalue = make_hash(lower_wellbore)
        # query to see if api14 and hash exist in db
        exists = db.wells.find_one( {"$and":[ {'api14': str(wellbore["api14"])}, {"hash_value":hashvalue}]} )
        # check and see if query returned any value from db
        if exists is None:
            # store hash in json object
            lower_wellbore['hash_value'] = hashvalue
            # insert into mongodb
            wellbores_to_update.append(copy.deepcopy(lower_wellbore))

    return wellbores_to_update




if __name__ == "__main__":

    c = Collector('well', 'well-driftwood')
    x  = c.get()
    apis = get_apis(x)
    if not apis:
        print("No Records To Insert!")
    else:
        db.wells.insert_many(apis)

