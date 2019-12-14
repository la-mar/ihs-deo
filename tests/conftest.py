# pylint: disable=missing-function-docstring,missing-module-docstring,no-self-use,unused-import
import os
import json

import pytest

# from collector.endpoint import Endpoint
# from collector.request import Request
# from collector.requestor import Requestor
# from collector.collector import Collector
from collector.endpoint import Endpoint
from config import TestingConfig

# app_config = TestingConfig()
# endpoints = collector.endpoint.load_from_config(app_config)
# functions = config.functions


@pytest.fixture
def conf():
    yield TestingConfig()


@pytest.fixture
def endpoint():
    yield Endpoint.from_dict(
        "test",
        {
            "enabled": True,
            "version": "v10",
            "model": "api.models.WellHorizontal",
            "exclude": [],
            "normalize": False,
            "options": {
                "data_type": "Well",
                "template": "EnerdeqML Well",
                "criteria": {"hole_direction": "H"},
            },
            "tasks": {
                "endpoint_check": {
                    "seconds": 60,
                    "options": {
                        "query_path": "well_by_api.xml",
                        "matrix": {"sequoia": {"api": "42461409160000"}},
                    },
                },
            },
        },
    )


@pytest.fixture
def endpoints():
    yield Endpoint.load_from_config(conf)


# @pytest.fixture()
# def functions(app_config):
#     yield app_config.functions


# @pytest.fixture()
# def endpoint(endpoints):
#     yield endpoints.get("complex")


# @pytest.fixture()
# def endpoint_simple(endpoints):
#     yield endpoints.get("simple")


# @pytest.fixture()
# def requestor(app_config, endpoint, functions):
#     yield Requestor(app_config.API_BASE_URL, endpoint, functions)


# @pytest.fixture()
# def req(app_config, requestor):
#     yield Request(
#         "GET",
#         f"{app_config.API_BASE_URL}/path/1/subpath/2/values",
#         headers={"Authorization": requestor.get_token()},
#     )


# @pytest.fixture()
# def nested_json(app_config):
#     path = os.path.join(app_config.CONFIG_BASEPATH, "nested_data.json")
#     with open(path, "r") as f:
#         return json.load(f)


# @pytest.fixture()
# def normalized_json(app_config):
#     path = os.path.join(app_config.CONFIG_BASEPATH, "normalized.json")
#     with open(path, "r") as f:
#         return json.load(f)
