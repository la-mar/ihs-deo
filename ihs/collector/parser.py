from __future__ import annotations
import functools
import logging
import re
from datetime import date
from pydoc import locate
from typing import Any, Callable, List, Union, Dict

import util
from config import get_active_config

conf = get_active_config()

logger = logging.getLogger(__name__)


def safe_convert(func):
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"{func} failed: {e}")
            return None

    return func_wrapper


# def get_default_rules():
#     ruledefs = conf.COLLECTOR_PARSER_RULES

#     rules = []
#     for name, rules in ruledefs.items():
#         for rule in rules:
#             RuleType = util.locate_resource(rule["type"])
#             rules.append(RuleType(rule["value"], rule["name"], name=name))

#     logger.debug(f"Loaded {len(rules)} rules")
#     return rules


def locate_resource(name: str) -> Callable:
    resource = globals()[name]
    return resource


class Criterion:
    def __init__(self, func: Callable, name: str = None):
        self.name = name or ""
        self.func = func

    def __call__(self, value: Any):
        return bool(self.func(value))

    def __repr__(self):
        return f"Criterion: {self.name} - {self.func}"


class RegexCriterion(Criterion):
    def __init__(self, regex: str, name: str = None):
        self.regex = re.compile(regex)
        super().__init__(func=self.regex.match, name=name)

    def __call__(self, value: Any):
        super().__call__(str(value))


class TypeCriterion(Criterion):
    def __init__(self, dtype: type, name: str = None):
        func = lambda v: isinstance(v, dtype)
        super().__init__(func=func, name=name)


class ValueCriterion(Criterion):
    def __init__(self, value: Union[str, int, float, bool], name: str = None):
        func = lambda v: v == value
        super().__init__(func=func, name=name)


class ParserRule:
    """ Parser rule base set """

    def __init__(self, criteria: List[Criterion], name: str = None, **kwargs):
        self.name = name or ""
        self.criteria = criteria

    def __call__(self, value: Any) -> Any:
        return all([c(value) for c in self.criteria])

    def __repr__(self):
        return f"ParserRule - {self.name}: {len(self.criteria)} criteria"

    @classmethod
    def from_list(cls, criteria: List[Dict], name: str = None) -> ParserRule:
        criteriaObjs: List[Criterion] = []
        for c in criteria:
            CriteriaType = locate_resource(c["type"])
            criteriaObjs.append(CriteriaType(c["value"], c["name"]))
        return cls(criteriaObjs, name=name)


class Parser:
    def __init__(self, rules: List[ParserRule], name: str = None):
        self.name = name or ""
        self.rules = rules

    def __repr__(self):
        return f"Parser - {self.name}: {len(self.rules)} rules"

    def add_rule(self, rule: ParserRule):
        self.rules.append(rule)

    def run_checks(self, value: Any):
        checks = []
        for rule in self.rules:
            result = rule(value)
            checks.append(result)
            if not result:
                logger.debug("Parser check failed: %s", (rule,))
        return all(checks)

    def parse(self, value: Any) -> Any:
        """ Attempt to parse a value if all criteria are met """
        return value if self.run_checks(value) else value

    @classmethod
    def init(cls, conf: Dict[str, List], name: str = None) -> Parser:
        rules: List[ParserRule] = []
        for cname, criteria in conf.items():
            rules.append(ParserRule.from_list(criteria, name=cname))

        return cls(rules, name=name)

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

    import util

    data = util.load_json("example.json")

    parser = Parser.init(conf.COLLECTOR_PARSER_RULES, name="default")

    test_values = [
        "2019-01-01",
        "1",
        "+1",
        "-1",
        "0",
        "+0",
        "-0",
        "11",
        "00",
        "01",
        "+11",
        "+00",
        "+01",
        "-11",
        "-00",
        "-01",
        "1234567890",
        "+1234567890",
        "-1234567890",
        "1.1034",
        "+1.1034",
        "-1.1034",
        "0.1034",
        "+0.1034",
        "-0.1034",
        "11.1034",
        "00.1034",
        "01.1034",
        "+11.1034",
        "+00.1034",
        "+01.1034",
        "-11.1034",
        "-00.1034",
        "-01.1034",
        "1234567890.1034",
        "+1234567890.1034",
        "-1234567890.1034",
        "2019-01-01",
        "19-01-01",
        "2019-01",
        "qwe2019-01-01",
        "2019-01-01rte",
        "3242019-01-01",
    ]
