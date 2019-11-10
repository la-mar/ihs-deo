from typing import Callable, Union
from util.stringprocessor import StringProcessor
import urllib.parse
import json


def transform_keys(data: dict, convert: Callable) -> dict:
    """
    Recursively goes through the dictionary data and replaces keys with the convert function.
    """
    if isinstance(data, (str, int, float)):
        return data
    if isinstance(data, dict):
        new = data.__class__()
        for k, v in data.items():
            new[convert(k)] = transform_keys(v, convert)
    elif isinstance(data, (list, set, tuple)):
        new = data.__class__(transform_keys(v, convert) for v in data)
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
    """load and return an xml file as a string

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
    except Exception as fe:
        print(f"Invalid filename: {path}")
    return xml


def to_json(d: dict, path: str, cls=None):
    with open(path, "w") as f:
        json.dump(d, f, cls=cls, indent=4)


def load_json():
    with open(path, "r") as f:
        return json.load(f)
