
import app.connection as conn
from app.connection import *
from app.util import *
from app.mongo import *

import os
import logging

from time import sleep
import xmltodict
import pprint
import json
from lxml import etree

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

WELL_TEMPLATE = """
    <EXPORT>
        <TEXTUAL_EXPORTS>
            <WELL_XML INCLUDE_PRODFIT='TRUE'>
            </WELL_XML>
        </TEXTUAL_EXPORTS>
    </EXPORT>"""


class Collector():
    """ One per query """

    _query_dir = 'queries/'
    _query_ext = '.xml'
    _template_dir = 'templates/'
    _soap_headers =

    def __init__(self, query_name: str):
        self.query_name = query_name
        self.query = self._load_query(self.query_name)

    def _load_query(self, name: str):
        """query name must equal file name"""

        criterias = None
        if not name.endswith(self._query_ext):
            name = name + self._query_ext

        try:
            with open(self._query_dir + name, 'r') as f:
                criterias = f.read()
        except Exception as fe:
            print(f'Invalid Query Name: {name}')

        return criterias


    def _make_params(self, datatype: str, query: str, template: str = None):
        return {
                'Domain':'US',
                'DataType': datatype,
                # 'Template': 'EnerdeqML Well',
                'Template': template,
                'Query': query
                }

    def _get_target(self):
        return {
                'Filename':'default',
                'Overwrite': 'True'
                }

    def is_complete(self, job_id):
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






