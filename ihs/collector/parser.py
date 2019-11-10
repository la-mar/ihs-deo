import functools
import re
from datetime import date, datetime
from typing import Callable, Union


def safe_convert(func):
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"{func} failed: {e}")
            return None

    return func_wrapper


class ValueParser:
    @staticmethod
    def patterns():
        return [
            {"pattern": re.compile(r"^[-+]?[0-9]+$"), "func": ValueParser.try_int,},
            {
                "pattern": re.compile(r"^[-+]?[0-9]*\.[0-9]+$"),
                "func": ValueParser.try_float,
            },
            {
                "pattern": re.compile(r"^\d\d\d\d-\d\d-\d\d$"),
                "func": ValueParser.try_date,
            },
        ]

    @staticmethod
    def parse(value: str) -> Union[int, float, str, None]:
        for mapping in ValueParser.patterns():
            pattern: re.Pattern = mapping.get("pattern")  # type: ignore
            func: Callable = mapping.get("func")
            result = pattern.match(value)
            if result:
                return func(result.group())
        return value

    @staticmethod
    @safe_convert
    def try_int(s: str) -> Union[int, None]:
        return int(float(s))

    @staticmethod
    @safe_convert
    def try_float(s: str) -> Union[float, None]:
        return float(s)

    @staticmethod
    @safe_convert
    def try_date(s: str) -> Union[date, None]:
        return date.fromisoformat(s)


if __name__ == "__main__":

    ValueParser.parse("2019-01-01")
    ValueParser.parse("1")

    ValueParser.parse("1")
    ValueParser.parse("+1")
    ValueParser.parse("-1")
    ValueParser.parse("0")
    ValueParser.parse("+0")
    ValueParser.parse("-0")
    ValueParser.parse("11")
    ValueParser.parse("00")
    ValueParser.parse("01")
    ValueParser.parse("+11")
    ValueParser.parse("+00")
    ValueParser.parse("+01")
    ValueParser.parse("-11")
    ValueParser.parse("-00")
    ValueParser.parse("-01")
    ValueParser.parse("1234567890")
    ValueParser.parse("+1234567890")
    ValueParser.parse("-1234567890")

    ValueParser.parse("1.1034")
    ValueParser.parse("+1.1034")
    ValueParser.parse("-1.1034")
    ValueParser.parse("0.1034")
    ValueParser.parse("+0.1034")
    ValueParser.parse("-0.1034")
    ValueParser.parse("11.1034")
    ValueParser.parse("00.1034")
    ValueParser.parse("01.1034")
    ValueParser.parse("+11.1034")
    ValueParser.parse("+00.1034")
    ValueParser.parse("+01.1034")
    ValueParser.parse("-11.1034")
    ValueParser.parse("-00.1034")
    ValueParser.parse("-01.1034")
    ValueParser.parse("1234567890.1034")
    ValueParser.parse("+1234567890.1034")
    ValueParser.parse("-1234567890.1034")

    ValueParser.parse("2019-01-01")
    ValueParser.parse("19-01-01")
    ValueParser.parse("2019-01")
    ValueParser.parse("qwe2019-01-01")
    ValueParser.parse("2019-01-01rte")
    ValueParser.parse("3242019-01-01wwe")
