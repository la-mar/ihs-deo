
from app.connection import *
from app.util import *
from time import sleep
import pandas as pd
import bs4

# , '2019/01/01', '2019/01/31'
querybuilder.service.GetDailyUpdateInterval()
xml = querybuilder.service.GetChangesAndDeletes('Well', '2019/01/01', '2019/02/01', 1, _soapheaders=[header_value])



def production_header_xml_to_df(xml: str) -> pd.DataFrame:
    soup = bs4.BeautifulSoup(xml, 'lxml-xml')

    root = soup.find('result-set')

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


    return pd.DataFrame(data = values, columns = column_names)


to_file(xml['Result'], 'changes_and_deletes.xml')
