from functools import partial


import bs4
import pandas as pd
import yaml
from datetime import datetime, date
from pydoc import locate
import arrow
from lxml.etree import _Element
from lxml import etree


from app.wells import driftwood_wells


MAPPING_DTYPES = {
    'int' : {
        'dtype':int,
        'func': 'to_int',
        },
    'float': {
        'dtype':float,
        'func': 'to_float',
        },
    'str' : {
        'dtype':str,
        'func': 'to_str',
        },
    'date' : {
        'dtype':arrow.arrow.Arrow,
        'func': 'to_arrow',
        },
    'datetime' :{
        'dtype': arrow.arrow.Arrow,
        'func': 'to_arrow',
        },
}

class DotDictMixin(dict):
    """Extension of the base dict class, adding dot.notation access to dictionary attributes and additional utility functions"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


    def flatten(self):
        """Wrapper for _flatten function for external use

        Returns:
            DotDictMixin
        """

        return self._flatten(self)

    def _flatten(self, d: dict):
        """Flattens the contents of the dictionary to a single dimension

        Arguments:
            d {dict} -- instance or subclass of dict

        Returns:
            DotDictMixin --  flattened (1 x n dimension) dictionary
        """

        def items():
            for key, value in d.items():
                if isinstance(value, DotDictMixin):
                    for subkey, subvalue in self._flatten(value).items():
                        yield key + "/" + subkey, subvalue
                else:
                    yield key, value

        return DotDictMixin(items())


def from_file(filename: str) -> str:
    xml = None
    with open(filename, "r") as f :
        xml = f.read().splitlines()
    return ''.join(xml)

def to_file(xml: str, filename: str) -> str:
    with open(filename, "w") as f:
        f.writelines(xml)

def names(attribute_group: list) ->  list:
    return [x.name for x in attribute_group.children]

def recurse_group(group):
    if isinstance(group, bs4.element.Tag):
        for child in group.children:
            print(group.name)
            return recurse_group(child.children)

def recurse(tag):
    if isinstance(tag, bs4.element.Tag):
        for child in list(tag.children):
            print(child.name)
            return recurse(child)

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

def child_names(tag):
    if isinstance(tag, bs4.element.Tag):
        return [t.name for t in tag.children if isinstance(t, bs4.element.Tag)]

def has_subtags(tag):
    if isinstance(tag, bs4.element.Tag):
        return any([isinstance(tag, bs4.element.Tag) for tag in tag.children])
    else:
        return False

def flatten(xml:bs4.element.Tag, table_name: str):
    data = []
    if xml is not None:
        for g in xml.recursiveChildGenerator():
            if isinstance(g, bs4.element.Tag):
                if not has_subtags(g):
                        d = '/'.join(list(reversed([x.name for x in g.parents])))
                        d += '/' + g.name + '||' + g.text
                        data.append(d)

        tokens = [x.split('/') for x in data]

        return data

def get_xpaths(flattened_list, sep = '||') -> list:
    return [x.split(sep)[0] for x in flattened_list]

def remove_xpath_prefix(flattened_list: list, table_name: str) -> list:

    ls = []
    for xpath in flattened_list:
        try:
            idx = xpath.index(table_name)
            ls.append(xpath[idx:])
        except:
            ls.append(xpath)

    return ls

def to_yaml(collection, filename):
    with open(filename, 'w') as f:
        # f.writelines(json.dumps(xpaths))
        yaml.dump(collection, f, default_flow_style=False)

def from_yaml(filename):
    with open(filename, 'r') as f:
        return yaml.load(f)



def xpaths_to_yaml(xpaths, filename):
    output = {}
    for x in xpaths:
        output[x] = {
            'table_name': None,
            'field_name': None,
            'attribute2': None,
            'attribute3': None,
            'attribute4': None,
            'attribute5': None,
        }
    to_yaml(output, filename)

def xml_to_yaml(soup, groupname, filename):
    flat = flatten(soup, groupname)
    flat = remove_xpath_prefix(flat, groupname)
    xpaths = get_xpaths(flat)
    xpaths_to_yaml(xpaths, filename)


def parse_groups():
    xml = from_file('well_header.xml')
    soup = bs4.BeautifulSoup(xml, 'lxml-xml')
    wellset = soup.find_all('WELLBORE')
    well = wellset[1]


    group_name = 'PRODUCING_ENTITY'
    filename = 'production_mappings'

    soup = soup.find(group_name)

    for x in child_names(soup):
        xml_to_yaml(soup.find(x), x, f'mappings/{x.lower()}_map.yaml')


def flatten_xsd(xml:bs4.element.Tag, table_name: str):
    data = []
    return data



# xml = from_file('C:\Repositories\Collector-IHS\well_header.xml')
# soup = bs4.BeautifulSoup(xml, 'lxml-xml')


# data = []
# if soup is not None:
#     for g in soup.recursiveChildGenerator():
#         if isinstance(g, bs4.element.Tag):



#             if not has_subtags(g):
#                     d = '/'.join(list(reversed([x.name for x in g.parents])))
#                     d += '/' + g.name + '||' + g.text
#                     data.append(d)

#     tokens = [x.split('/') for x in data]


# soup.find(attrs = {'name': 'MONTH'}).has_attr('name')


root = etree.XML(xml.encode())


tree = root.getroottree()
i = tree.getiterator()




# Import mapping
MAP_PATH = 'mappings\well\PB_WELL_TEST_map.yaml'

def load_mapping(filepath: str) -> dict:
    mp = from_yaml(filepath)
    # for name, mapping in mp.items():
    #     mapping['dtype'] = MAPPING_DTYPES[mapping['dtype']]

    return mp

def to_arrow(value: str, _format: str = None) -> arrow.arrow.Arrow:
    if _format:
        return arrow.get(value, _format)
    else:
        return arrow.get(value)

def to_int(value: str) -> int:
    try:
        result = int(value)
    except:
        result = int(float(value))

    return result

def to_float(value: str) -> float:
    return float(value)

def _locate(func_name: str):
    return globals()[func_name]

def to_dtype(value: str, dtype: str):
    if dtype in MAPPING_DTYPES.keys():
        mapping: dict = MAPPING_DTYPES[dtype]

        func = _locate(mapping['func'])
        casted_value = func(value)

        if isinstance(casted_value, mapping['dtype']):
            value = casted_value
        else:
            print('Incorrect type of casted value.')
    else:
        print('Invalid dtype')
    return value

def to_str(value):
    if not isinstance(value, str):
        value = str(value)

    # TODO: Do some generic string processing here (e.g. remove leading/trailing/duplicate whitespace)

    return value



def extract_apis(tag: _Element):
    # get apis from header tag attributes
    api_tags = [x for x in tag.iterdescendants() if x.tag == 'IDENTIFICATION']
    apis = {}
    for tag in api_tags:
        if 'TYPE' in tag.attrib:
            apis[tag.attrib['TYPE']] = tag.text
    return apis

def get_identifier(preferences: list, options: dict):
    for p in preferences:
        try:
            return options[p]
        except:
            print(f'{p} not in {options.keys()}')

    return None

def descendants_xpaths(tag: _Element):
    for e in tag.iterdescendants():
        if len(list(e.getchildren())) == 0:
            print(tree.getpath(e))

def get_test_root(wellbore_tag: _Element):
    test_root_tag = wellbore_tag.find('TESTS')
    return test_root_tag

def get_test_tags(test_root: _Element):
    if test_root is not None:
        tags = list(test_root.iterchildren())
    else:
        tags = []

    return tags

def extract_tests(wellbore_tag: _Element, mapping: dict, as_df: bool = True):
    apis = extract_apis(wellbore_tag)
    print(apis)
    test_root_tag = get_test_root(wellbore_tag)
    test_tags = get_test_tags(test_root_tag)

    tests = []
    for tag in test_tags:
        tests.append(extract_test_data(tag, mapping, apis))


    if as_df:
        tests = pd.DataFrame.from_records(tests)

    return tests

def extract_test_data(test_tag: _Element, mapping: dict, apis: dict) -> dict:
    test_data = {}
    test_data['type'] = test_tag.attrib['TYPE_CODE']
    test_data['uwi'] = get_identifier(['UWI'], apis)
    for xpath, mp in mapping.items():
        elements: list = wellbore_tag.xpath(xpath) # fetches element via xpath unique among other tests in this wellbore
        if len(elements) > 0:
            value = elements[0].text
            test_data[mp['field_name']] = to_dtype(value, mp['dtype'])

    return test_data




""" Construct well tests table """

# select nodes from iterator based on tag name
wellbores = [x for x in tree.getiterator() if x.tag == 'WELLBORE']

# Get single wellbore
wellbore_tag = wellbores[4]

# get apis from header tag attributes



# Import mapping
tests_mapping = load_mapping(MAP_PATH)

test_data: list = extract_tests(wellbore_tag, tests_mapping)


tests = pd.DataFrame()
for wellbore in wellbores:
    tests = tests.append(extract_tests(wellbore, tests_mapping))



from app.tables import Pb_Well_Test



Pb_Well_Test.merge_records(tests)
a

# Iter tests

