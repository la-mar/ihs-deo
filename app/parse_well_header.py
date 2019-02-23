import bs4
import pandas as pd

from app.wells import driftwood_wells

xml = driftwood_wells()

soup = bs4.BeautifulSoup(xml, 'lxml-xml')
soup.find_all('WELLBORES')






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



