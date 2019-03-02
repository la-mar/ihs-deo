import bs4
import pandas as pd
import yaml

from app.wells import driftwood_wells


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



xml = from_file('docs\DirectConnect\Data Export Formats 2018 v10\Data Export Formats 2018 v10\EnerdeqML Format\EnerdeqML_v1.20_Production.xsd')
soup = bs4.BeautifulSoup(xml, 'lxml-xml')


data = []
if soup is not None:
    for g in soup.recursiveChildGenerator():
        if isinstance(g, bs4.element.Tag):



            if not has_subtags(g):
                    d = '/'.join(list(reversed([x.name for x in g.parents])))
                    d += '/' + g.name + '||' + g.text
                    data.append(d)

    tokens = [x.split('/') for x in data]


soup.find(attrs = {'name': 'MONTH'}).has_attr('name')


from lxml import etree

root = etree.XML(xml.encode())

#! %hist
# root = etree.XML(xml)
# from lxml import etree
# root = etree.XML(xml)
# root = etree.XML(xml.encode())
# root
#     xml = from_file('producing_entity.xml')
# root = etree.XML(xml.encode())
# root = etree.XML(xml)
# xml
#     xml = from_file('producing_entity.xml')
# root = etree.XML(xml)
#     xml = from_file('well_header.xml')
# root = etree.XML(xml)
# root = etree.XML(xml.encode())
# dir(root)
# root.nsmap
# root.getroottree
# root.getroottree()
# root.get
# %pdef root.get
# %pdef root.get('HEADER')
# %pdef root.get('WELLBORE')
# root.getChildren()
# root
# dir(root)
# root.getchildren()
# wb = root.getchildren()[-1]
# wb
# wb.getchildren()
# head = wb.getchildren()[1]
# head
# head.getchildren()
# head.getchildren().getPath()
# head.getchildren()[0].getpath()
# head.getchildren()[0].getPath()
# dir(head.getchildren()[0])
# head.getchildren()[0].xpath
# head.getchildren()[0].xpath()
# head.getchildren()[0].xpath(head)
# tree = root.getroottree()
# tree.getpath()
# tree.getpath(tree)
# tree
# tree.getchildren
# dir(tree)
# tree.find(head.getchildren()[0])
# tree.getelementpath
# tree.getelementpath()
# dir(root)
# root.tag