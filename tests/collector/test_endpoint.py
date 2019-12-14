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

    def test_load_from_config(self, conf):
        Endpoint.load_from_config(conf)

    # def test_load_from_config_has_endpoints(self):
    #     Endpoint.load_from_config({})

    def test_locate_model(self, endpoint):
        assert issubclass(endpoint.model, me.Document)

    def test_locate_model_from_globals(self, endpoint):
        assert endpoint.locate_model("pytest")

    def test_locate_model_not_found(self, endpoint):
        with pytest.raises(ModuleNotFoundError):
            endpoint.locate_model("not_a_real_model")
