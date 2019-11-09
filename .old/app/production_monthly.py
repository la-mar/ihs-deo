from app.collector import Collector
from time import sleep
from app.util import *
from app.mongo import *
import xmltodict
import pprint
import json
from lxml import etree, objectify
import copy


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


def elevate_api(record: dict) -> dict:
    """ Moves a well's identification number (api) to the top level of
        the dictionary."""

    api = record["METADATA"]["IDENTIFICATION"]
    if len(api) == 14:
        record["api14"] = api
        record["api10"] = api[:10]
    elif len(api) == 10:
        record["api10"] = api
        record["api14"] = api + "0000"

    # move new elements to beginning of ordered dict
    record.move_to_end("api14", last=False)
    record.move_to_end("api10", last=False)

    return record


def get_apis(encoded_xml):
    xml = objectify.fromstring(encoded_xml)
    root = xml.getroottree().getroot()
    records = [child for child in root.getchildren() if child.tag == "PRODUCING_ENTITY"]

    prod_ent_to_update = []
    # iterate through production objects
    number_of_records = len(records)
    for i in range(number_of_records):
        # convert child into dictionary
        xmltojson = etree.tostring(records[i])
        production_record = xmltodict.parse(xmltojson)["PRODUCING_ENTITY"]
        # format json object
        lower_prodrecord = tolower(elevate_api(production_record))
        # create hash of formatted json object
        hashvalue = make_hash(lower_prodrecord)
        # query to see if api14 and hash exist in db
        exists = db.production.find_one(
            {
                "$and": [
                    {"api14": str(production_record["api14"])},
                    {"hash_value": hashvalue},
                ]
            }
        )
        # check and see if query returned any value from db
        if exists is None:
            # store hash in json object
            lower_prodrecord["hash_value"] = hashvalue
            # insert into mongodb
            prod_ent_to_update.append(copy.deepcopy(lower_prodrecord))

    return prod_ent_to_update


if __name__ == "__main__":
    c = Collector("production allocated", "production-driftwood", "production.xml")
    x = c.get()
    apis = get_apis(x)
