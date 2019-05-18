from app.connection import *
from app.util import *
from app.mongo import *


from time import sleep
import xmltodict
import pprint
import json
from lxml import etree, objectify

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


import types
def lowerValues(arg):
    print(arg)
    # Handle iterables
    if isinstance(arg, list):
        return [lowerValues(item) for item in arg]
    elif isinstance(arg, str):
        return arg.lower()
    else:
        return arg

from collections import OrderedDict
def renameKeysToLower(iterable):
    iterable = dict(iterable).copy()
    if type(iterable) is dict:
        for key in iterable.keys():
            iterable[key.lower()] = iterable.pop(key)
            if type(iterable[key.lower()]) is dict or type(iterable[key.lower()]) is list:
                iterable[key.lower()] = renameKeysToLower(iterable[key.lower()])
    elif type(iterable) is list:
        for item in iterable:
            item = renameKeysToLower(item)
    return dict(iterable)

def tolower(d: dict):
    result = {}
    for key, value in d.items():
        if issubclass(type(value), dict):
            result[key.lower()] = tolower(value)
        else:
            # return {k.lower():v for k, v in d.items()}
            result[key.lower()]

def dictify(group): #! Nope
    result = {}
    for li in list(group.children):
        key = li.name
        if key is not None:
            if key in list(result.keys()): # key exists
                if isinstance(li, bs4.element.Tag): # is tag
                    if isinstance(result[key], list): # is list
                        result[key].append(li.name)
                    else:
                        result[key] = dictify(li)

                elif isinstance(result[key], list): # is list
                        result[key].append(li.name)
                else: # is str
                    result[key] = [result[key], li.name]
            else:
                if isinstance(li, bs4.element.Tag): # is tag
                    result[key] = dictify(li)
                elif isinstance(result[key], list): # is list
                        result[key].append(li.name)
                else:
                    result[key] = li
        else:
            return li
    return result


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

    lower_wellbore = {lowerValues(k) : v for k,v in wellbore.items()}

    # for key, value in ids.items():
    #     wellbore.update({x['@TYPE']: x['#text']})
    #     wellbore.move_to_end(x['@TYPE'], last=False)

    #to_file(json.dumps(wellbore, indent = 4), 'wellbore.json')
    # write to mongodb
    #db.wells.insert(wellbore)

    #x = db.wells.find_one({'api14': '42383374130000'})

data = tolower(wellbore)




