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




[c.attrs.update({'type': 'attribute_group'}) for c in subgroups]

record_meta = soup.find('record-meta')
meta_attributes = record_meta.find_all('attribute')
column_names: list = [x.attrs['alias'] for x in meta_attributes if x.has_attr('alias')]

xml_records: list = soup.find_all('record')

values: list = []
for record in xml_records:
    vals = []
    for attribute in record:
        text = attribute.text
        if text == '':
            text = None
        vals.append(text)
    values.append(vals)

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


def dictify(group):
    result = {}
    for li in list(group.children):
        key = li.name
        if key is not None:
            if isinstance(li, bs4.element.Tag):
                result[key] = dictify(li)
            else:
                result[key] = li
        else:
            return li
    return result


def dictify(ul):
    result = {}
    flat = []
    for li in list(ul.children):
        key = li.name
        if key is not None:
            if isinstance(li, bs4.element.Tag):
                flat += dictify(li)
            else:
                flat += li
        else:
            return li

    return flat
