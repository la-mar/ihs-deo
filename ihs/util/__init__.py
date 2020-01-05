import logging
import json
import urllib.parse
from typing import Callable, Union, Tuple

from util.stringprocessor import StringProcessor
from util.jsontools import DateTimeEncoder

logger = logging.getLogger(__name__)


def apply_transformation(
    data: dict, convert: Callable, keys: bool = False, values: bool = True
) -> dict:
    """ Recursively apply the passed function to a dict's keys, values, or both """
    if isinstance(data, (str, int, float)):
        if values:
            return convert(data)
        else:
            return data
    if isinstance(data, dict):
        new = data.__class__()
        for k, v in data.items():
            if keys:
                new[convert(k)] = apply_transformation(v, convert, keys, values)
            else:
                new[k] = apply_transformation(v, convert, keys, values)
    elif isinstance(data, (list, set, tuple)):
        new = data.__class__(
            apply_transformation(v, convert, keys, values) for v in data
        )
    else:
        return data
    return new


def from_file(filename: str) -> str:
    xml = None
    with open(filename, "r") as f:
        xml = f.read().splitlines()
    return "".join(xml)


def to_file(xml: str, filename: str):
    with open(filename, "w") as f:
        f.writelines(xml)


def urljoin(base: str, path: str) -> str:
    if not base.endswith("/"):
        base = base + "/"
    if path.startswith("/"):
        path = path[1:]
    return urllib.parse.urljoin(base, path)


def load_xml(path: str) -> Union[str, None]:
    """ Load and return an xml file as a string

    Arguments:
        filename {str} -- filename of xml file. extension is optional.

    Returns:
        [type] -- [description]
    """

    xml = None
    ext = ".xml"
    if not path.endswith(ext):
        path = path + ext

    try:
        with open(path, "r") as f:
            xml = f.read()
    except FileNotFoundError as fe:
        print(f"Invalid file path: {fe}")
    return xml


def to_json(d: dict, path: str, cls=DateTimeEncoder):
    with open(path, "w") as f:
        json.dump(d, f, cls=cls, indent=4)


def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)


def query_dict(path: str, data: dict, sep: str = "."):
    elements = path.split(sep)
    for e in elements:
        if issubclass(type(data), list) and len(data) > 0:
            data = data[-1]  # TODO: this needs to be smarter
        if not issubclass(type(data), dict):
            logger.debug(f"{data} ({type(data)}) is not a subclass of dict")
            data = {}
            # raise ValueError(f"{data} ({type(data)}) is not a subclass of dict")
        data = data.get(e, {})
    return data if data != {} else None


def gal_to_bbl(value: float, uom: str) -> Tuple[float, str]:
    if uom.lower() == "gal":
        return value / 42, "BBL"
    else:
        return value, uom
