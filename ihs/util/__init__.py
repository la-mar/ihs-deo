import hashlib
import json
import logging
import urllib.parse
from collections import OrderedDict
from typing import Any, Callable, List, Tuple, Union, Iterable, Generator
import itertools

from util.jsontools import DateTimeEncoder
from util.stringprocessor import StringProcessor

logger = logging.getLogger(__name__)


def make_hash(data: Union[List, OrderedDict]) -> str:
    return hashlib.md5(str(data).encode()).hexdigest()


def ensure_list(value: Any) -> List[Any]:
    if not issubclass(type(value), list):
        return [value]
    return value


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


def to_bool(value):
    valid = {
        "true": True,
        "t": True,
        "1": True,
        "yes": True,
        "no": False,
        "false": False,
        "f": False,
        "0": False,
    }

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if not isinstance(value, str):
        value = str(value)

    lower_value = value.lower()
    if lower_value in valid:
        return valid[lower_value]
    else:
        raise ValueError('invalid literal for boolean: "%s"' % value)


def to_int(s: str) -> Union[int, None]:
    if s is None:
        return None
    if isinstance(s, str):
        s = float(s)  # type: ignore
    return int(s)


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


# def query_dict(path: str, data: dict, sep: str = "."):
#     elements = path.split(sep)
#     for e in elements:
#         if issubclass(type(data), list) and len(data) > 0:
#             data = data[-1]  # TODO: this needs to be smarter
#         if not issubclass(type(data), dict):
#             logger.debug(f"{data} ({type(data)}) is not a subclass of dict")
#             data = {}
#             # raise ValueError(f"{data} ({type(data)}) is not a subclass of dict")
#         data = data.get(e, {})
#     return data if data != {} else None


def query_dict(path: str, data: dict, sep: str = "."):
    elements = path.split(sep)
    for e in elements:
        if issubclass(type(data), list) and len(data) > 0:
            # logger.warning(f"e={e}, data={data}")
            try:
                data = data[int(e)]  # TODO: this needs to be smarter
            except ValueError:
                # handle cases where a list of items occurs where a mapping should be
                data = data[-1]
        elif issubclass(type(data), dict):
            data = data.get(e, {})

    return data if data != {} else None


def gal_to_bbl(value: float, uom: str) -> Tuple[float, str]:
    if uom.lower() == "gal":
        return value / 42, "BBL"
    else:
        return value, uom


def chunks(iterable: Iterable, n: int = 1000, cls=list) -> Generator:
    """ Process an infinitely nested interable in chunks of size n (default=1000) """
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield cls(itertools.chain((first_el,), chunk_it))
