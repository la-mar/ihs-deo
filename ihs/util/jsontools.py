from typing import Any, Dict, List, Union
from pathlib import Path

import json
from datetime import date, datetime, timedelta


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


class ObjectEncoder(json.JSONEncoder):
    """Class to convert an object into JSON."""

    def default(self, obj: Any):
        """Convert `obj` to JSON."""
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            return obj.__class__.__name__
        elif hasattr(obj, "tb_frame"):
            return "traceback"
        elif isinstance(obj, timedelta):
            return obj.__str__()
        else:
            # generic, captures all python classes irrespective.
            cls = type(obj)
            result = {
                "__custom__": True,
                "__module__": cls.__module__,
                "__name__": cls.__name__,
            }
            return result


class UniversalEncoder(DateTimeEncoder, ObjectEncoder):
    pass


def to_string(data: Union[List, Dict], pretty: bool = True) -> str:
    indent = 4 if pretty else 0
    return json.dumps(data, indent=indent, cls=UniversalEncoder)


def dumps(data: Union[List, Dict], pretty: bool = True) -> str:
    """ placeholder: alias for jsontools.to_string """
    return to_string(data, pretty)


def to_json(d: dict, path: Union[Path, str], cls=DateTimeEncoder):
    with open(path, "w") as f:
        json.dump(d, f, cls=cls, indent=4)


def load_json(path: Union[Path, str]):
    with open(path, "r") as f:
        return json.load(f)


def make_repr(data: Union[List, Dict], pretty: bool = True) -> str:
    """wraps to_string to encapsulate repr specific edge cases """
    return dumps(data=data, pretty=pretty)
