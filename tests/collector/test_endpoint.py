import pytest  # pylint: disable=unused-import

import mongoengine as me

from collector.endpoint import Endpoint

# pylint: disable=missing-function-docstring,missing-module-docstring,no-self-use


@pytest.fixture
def task_defs():
    return {
        "endpoint_check": {
            "seconds": 60,
            "options": {
                "query_path": "well_by_api.xml",
                "matrix": {"sequoia": {"api": "42461409160000"}},
            },
        },
    }


class TestEndpoint:
    def test_create_endpoint(self):
        Endpoint("test", "well_horizontal")

    def test_endpoint_repr(self, endpoint):
        repr(endpoint)

    def test_endpoint_iter(self, endpoint):
        d = dict(endpoint)
        assert isinstance(d, dict)
        assert len(d.keys()) > 0

    def test_load_from_config(self, conf):
        Endpoint.load_from_config(conf)

    def test_load_from_empty_config(self):
        with pytest.raises(AttributeError):
            assert Endpoint.load_from_config({}) == {}

    def test_load_from_config_bad_endpoint(self):
        class Conf:
            endpoints = {None: None}

        Endpoint.load_from_config(Conf())

    def test_locate_model(self, endpoint):
        import logging

        logger = logging.getLogger("endpoint")
        logger.setLevel(10)
        assert issubclass(endpoint.model, me.Document)

    def test_locate_model_from_globals(self, endpoint):
        assert endpoint.locate_model("pytest")

    def test_locate_model_not_found(self, endpoint):
        with pytest.raises(ModuleNotFoundError):
            endpoint.locate_model("not_a_real_model")

