
from app.connection import IHSConnector
from app.connection import *
from app.util import *
from app.mongo import *

import os
import logging

from time import sleep
import xmltodict
import pprint
import json
import lxml

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Mapping(dict):
    pass

class Collector():
    """ One per query """

    _query_dir = 'queries/'
    _query_ext = '.xml'
    _template_dir = 'templates/'
    _connection = None
    _query = None
    _template = None
    _attempts = 0
    _attempts_max = 3

    # TODO: Refactor to class
    _mappings = {'tags':
                    { # maps datatype to its expected tag name
                    'Well' : 'WELLBORE',
                    'Production Allocated': 'PRODUCING_ENTITY' # need to verify
                    },
                'default_templates' :
                    {
                    'Well': 'well.xml',
                    'Production Allocated': '???'
                    }
        }


    def __init__(self,
                 datatype: str,
                 query_name: str,
                 template_name: str = 'default',
                 poll: int = 5
                 ):
        self.datatype = datatype
        self.query_name = query_name
        self.template_name = template_name
        self.poll = poll
        self.job_id = -1
        self.raw = None

    @property
    def tag(self):
        return self._lookup_mapping('tags')

    @property
    def attempts_max(self):
        return self._attempts_max

    @attempts_max.setter
    def attempts_max(self, value: int):
        if value > 0:
            self._attempts_max = value
        else:
            print('Value for max attempts must be greater than 0')

    @property
    def attempts(self):
        return self._attempts

    @property
    def connection(self):
        """Singleton reference for the data source connection"""
        if self._connection is None:
            self._connection = IHSConnector()
        return self._connection

    @property
    def target(self, filename: str = 'default', overwrite: bool = True):
        return {
                'Filename':filename,
                'Overwrite': overwrite
               }

    @property
    def query(self):
        """Singleton reference for the query xml text"""
        if self._query is None:
            self._query = self._load_xml(self._query_dir, self.query_name)
        return self._query

    @property
    def template(self):
        """Singleton reference for the template xml text"""
        template_name = self.template_name
        if self.template_name == 'default':
            template_name = self._lookup_mapping('default_templates')

        return self._load_xml(self._template_dir, template_name)

    @property
    def is_complete(self):
        return self.connection.is_complete(self.job_id)

    @property
    def params(self):
        return {
                'Domain':'US',
                'DataType': self.datatype,
                'Template': self.template,
                'Query': self.query
                }

    def _lookup_mapping(self, map_key: str):
        """ Formats the input key with title case for marching"""
        value = None
        mapping = self._mappings.get(str(map_key), None) # get level 0
        if isinstance(mapping, dict):
            value = mapping.get(self.datatype.title(), None) # get level 1
        else:
            value = mapping
        return value


    def _load_xml(self, dir_path: str, filename: str):
        """load and return an xml file as a string

        Arguments:
            filename {str} -- filename of xmlfile. extension is optional.

        Returns:
            [type] -- [description]
        """

        xml = None
        ext = '.xml'
        if not filename.endswith(ext):
            filename = filename + ext

        try:
            with open(os.path.join(dir_path, filename), 'r') as f:
                xml = f.read()
        except Exception as fe:
            print(f'Invalid filename: {filename}')

        return xml


    def normalize_keys(self, d: dict):
        """Recursively transform all keys in a nested dictionary to lower case"""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key.lower()] = self.tolower(value)
            elif isinstance(value, list):
                result[key.lower()] = [self.tolower(x) for x in value]
            else:
                result[key.lower()] = value
        return result

    def elevate_api(self, entity: dict) -> dict:
        """ Moves a well's identification number (api) to the top level of
            the dictionary."""

        api = entity['METADATA']['IDENTIFICATION']
        if len(api) == 14:
            entity['api14'] = api
            entity['api10'] = api[:10]
        elif len(api) == 10:
            entity['api10'] = api
            entity['api14'] = api + '0000'

        #move new elements to beginning of ordered dict
        entity.move_to_end('api14', last=False)
        entity.move_to_end('api10', last=False)

        return entity

    # TODO: asyncio
    def _build_export(self, decode: bool = False, encoding: str = 'utf-8'):
        self.job_id = self.connection.build_export(self.params, self.target)

        while not self.is_complete:
            logger.debug(f'Sleeping for {self.poll} secs')
            sleep(self.poll)

        data = self.connection.get_export(self.job_id)

        if decode:
            data =  data.decode(encoding)

        return data

    def as_xml(self):
        """Transform the raw data and return it as processed xmlself.

            Examples:
                Well: The results of a well query will be reduced to element trees
                        beginning at a WELLBORE element, then returned as an xml string.

                Production: The results of a well query will be reduced to element
                            trees beginning at a PRODUCING_ENTITY element, then
                            returned as an xml string.

            Returns:
                str - a string of xml
        """
        raw = self.raw or self.get()
        xml = lxml.objectify.fromstring(raw)
        root = xml.getroottree().getroot()
        xml = [child for child in root.getchildren() if child.tag == self.tag()]
        return xml

    def as_json(self):
        return [xmltodict.parse(xml) for xml in self.as_xml()]

    def get(self):
        """Get the data"""
        self.raw = self._build_export()
        return self.raw



c = Collector('well', 'well-driftwood')

c.get()


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




# if __name__ == "__main__":

#     """wells_xml = driftwood_wells()

#     wells_json = json.dumps(xmltodict.parse(wells_xml), indent = 4)
#     to_file(wells_json, 'wells_json.json')
#     """



#     # from lxml import objectify
#     wells_bin = driftwood_wells(decode = False)
#     xml = objectify.fromstring(wells_bin)
#     root = xml.getroottree().getroot()
#     wellbores = [child for child in root.getchildren() if child.tag == 'WELLBORE']
#     c = wellbores[0]
#     # wellbores = xmltodict.parse(c)

#     #convert child into dictionary
#     xmltojson = lxml.etree.tostring(c)
#     wellbore = xmltodict.parse(xmltojson)['WELLBORE']



#     to_file(json.dumps(wellbore, indent = 4), 'wellbore.json')
#     # write to mongodb
#     db.wells.insert(wellbore)

#     x = db.wells.find_one({'api14': '42383374130000'})






