import bs4
import pandas as pd

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




xml = driftwood_wells()

soup = bs4.BeautifulSoup(xml, 'lxml-xml')
wellset = soup.find_all('WELLBORE')
wb = wellset[0]
subgroups = list(wb.children)
group = subgroups[1]

def names(attribute_group: list) ->  list:
    return [x.name for x in attribute_group.children]




# [c.attrs.update({'type': 'attribute_group'}) for c in subgroups]

# record_meta = soup.find('record-meta')
# meta_attributes = record_meta.find_all('attribute')
# column_names: list = [x.attrs['alias'] for x in meta_attributes if x.has_attr('alias')]

# xml_records: list = soup.find_all('record')

# values: list = []
# for record in xml_records:
#     vals = []
#     for attribute in record:
#         text = attribute.text
#         if text == '':
#             text = None
#         vals.append(text)
#     values.append(vals)

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




ops = group.contents[2]
ops = group

# data = {}

# ls = list(reversed([x.name for x in sg.parents]))
# list(reversed(ls))


def flatten(xml:bs4.element.Tag, table_name: str):
    data = []
    for g in ops.recursiveChildGenerator():
        if isinstance(g, bs4.element.Tag):
            d = '/'.join(list(reversed([x.name for x in g.parents])))
            d += '/' + g.name + '/' + g.text
            data.append(d)

    tokens = [x.split('/') for x in data]

    # table_name = 'HEADER'
    final = {}
    for _set in tokens:
        # _ = None
        while(_set[0] != table_name):
            _set.pop(0)

        final['_'.join([x for x in _set[:-1] if x != table_name]).lower()] = _set[-1]
        # _set = '_'.join(_set[])
        # print(_set)
    return data

flatten(group.contents[0], 'HEADER')
    # _set = '_'.join(_set[])
    # print(_set)



# from xmljson import badgerfish as bf
# from xml.etree.ElementTree import fromstring

# x = bf.data(fromstring(xml))
