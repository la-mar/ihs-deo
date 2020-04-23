from __future__ import annotations

import functools
import logging
import re
from datetime import datetime
from pydoc import locate
from typing import Any, Callable, Dict, List, Union

import util
from util.deco import safe_convert
from config import get_active_config

conf = get_active_config()

logger = logging.getLogger(__name__)



def locate_resource(name: str) -> Callable:
    """ Locate a resource (module, func, etc) within the module's namespace """
    resource = globals()[name]
    return resource


class Criterion:
    """ Basic component of validation logic used to compose a parsing rule """

    def __init__(self, func: Callable, name: str = None):
        self.name = name or ""
        self.func = func

    def __call__(self, value: Any):
        return bool(self.func(value))

    def __repr__(self):
        return f"Criterion: {self.name} - {self.func}"


class RegexCriterion(Criterion):
    """ Regex extraction harness for parser rule"""

    def __init__(self, regex: str, name: str = None):
        self.pattern = regex
        self.regex = re.compile(regex)
        super().__init__(func=self.regex.match, name=name)

    def __call__(self, value: Any):
        return super().__call__(str(value))

    def __repr__(self):
        return f"RegexCriterion: {self.name} - {self.pattern}"


class TypeCriterion(Criterion):
    """ Type check harness for parser rule """

    def __init__(self, dtype: type, name: str = None):
        func = lambda v: isinstance(v, dtype)
        super().__init__(func=func, name=name)


class ValueCriterion(Criterion):
    """ Value comparison harness for parser rule """

    def __init__(self, value: Union[str, int, float, bool], name: str = None):
        func = lambda v: v == value
        super().__init__(func=func, name=name)


class ParserRule:
    """ Validation rule used by a Parser to determine if/how to parse a value """

    def __init__(
        self,
        criteria: List[Criterion],
        name: str = None,
        allow_partial: bool = True,
        **kwargs,
    ):
        """
        Arguments:
            criteria {List[Criterion]} -- Criteria list

        Keyword Arguments:
            name {str} -- Rule name
            partial {bool} -- If True, the rule will pass if any criteria are satisfied. If False, the rule will pass only if all criteria are satisfied.

        """
        self.name = name or ""
        self.criteria = criteria
        self.allow_partial = allow_partial

    def __call__(
        self, value: Any, return_partials: bool = False
    ) -> Union[bool, List[bool]]:
        """ Enables the ParserRule to be callable, such that invoking the rule with
            a passed value will return the evaluation result of the called rule.

            Example: MyIntegerParserRule("13") -> True

            return_partials: set to True to return a list of the result of each criteria.
                             if set to False (default), return the result of the appropriate
                             boolean operation (any([partial1, partial2, ...]) if self.allow_partials = True (defualt))
                             or (all([partial1, partial2, ...]) otherwise).
        """
        partials = [c(value) for c in self.criteria]
        if return_partials:
            return partials
        if self.allow_partial:
            return any(partials)
        else:
            return all(partials)

    @property
    def match_mode(self):
        """ Determins if all criteria must be satisfied to consider a parse successful """
        return "PARTIAL" if self.allow_partial else "FULL"

    def __repr__(self):

        return f"ParserRule:{self.name} ({self.match_mode}) -  {len(self.criteria)} criteria"

    @classmethod
    def from_list(cls, criteria: List[Dict], **kwargs) -> ParserRule:
        """ Initialize a rule from a list of criteria specifications.
                Example criteria spec:
                    criteria = \
                        [
                            {
                                "name": "parse_integers",
                                "type": "RegexCriterion",
                                "value": r"^[-+]?[0-9]+$",
                            },
                        ],
         """
        criteriaObjs: List[Criterion] = []
        for c in criteria:
            CriteriaType = locate_resource(c["type"])
            criteriaObjs.append(CriteriaType(c["value"], c["name"]))
        return cls(criteriaObjs, **kwargs)


class Parser:
    """ Parses text values according to a set of arbitrary rules """

    def __init__(
        self, rules: List[ParserRule], name: str = None, parse_dtypes: bool = True
    ):
        self.name = name or ""
        self.rules = rules
        self.parse_dtypes = parse_dtypes

    def __repr__(self):
        return f"Parser - {self.name}: {len(self.rules)} rules"

    @classmethod
    def init(cls, ruleset: Dict[str, List], name: str = None) -> Parser:
        """ Initialize from a configuration dict """
        rules: List[ParserRule] = []
        for ruledef in ruleset:
            rules.append(ParserRule.from_list(**ruledef))  # type: ignore
        return cls(rules, name=name)

    @staticmethod
    @safe_convert
    def try_int(s: str) -> Union[int, None]:
        # if str(s).replace("+", "").replace("-", "").isdigit():
        # return int(float(s))
        return int(s)

    @staticmethod
    @safe_convert
    def try_float(s: str) -> Union[float, None]:
        return float(s)

    @staticmethod
    @safe_convert
    def try_date(s: str) -> Union[datetime, None]:
        return datetime.fromisoformat(s)

    def add_rule(self, rule: ParserRule):
        self.rules.append(rule)

    def run_checks(
        self, value: Any, return_partials: bool = False
    ) -> Union[bool, List[bool]]:
        """ Check if all parsing rules are satisfied """
        checks = []
        for Rule in self.rules:
            result = Rule(value)
            checks.append(result)
            if not result:
                logger.debug("Parser check failed: %s", (Rule,))
            else:
                logger.debug("Parser check passed: %s", (Rule,))

        return all(checks) if not return_partials else checks

    def parse_dtype(self, value: str) -> Union[int, float, str, datetime]:
        return self.try_int(value) or self.try_float(value) or self.try_date(value)

    def parse(self, value: Any) -> Any:
        """ Attempt to parse a value if all checks are satisfied """
        if not self.run_checks(value):
            return value
        else:
            return self.parse_dtype(value) if self.parse_dtypes else value


if __name__ == "__main__":

    parser = Parser.init(
        conf.PARSER_CONFIG["parsers"]["default"]["rules"], name="default"
    )

    print(parser.rules[0].criteria)

    test_values = [
        "2019-01-01",
        "1",
        "+1",
        "-1",
        "2018",
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
        "2020-06-06",
        "19-01-01",
        "2019-01",
        "qwe2019-01-01",
        "2019-01-01rte",
        "3242019-01-01",
        "31.24141",
        "101.98853",
        "+31.24141",
        "-101.98853",
    ]

    for value in test_values:
        new_value = parser.parse(value) or "-"
        value = value or "-"
        print(f"{value:<20} -> {new_value}")
