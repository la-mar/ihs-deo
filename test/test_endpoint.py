# pylint: disable=missing-function-docstring,missing-module-docstring,no-self-use
import pytest  # pylint: disable=unused-import

# from collector.endpoint import Endpoint, load_from_config


class TestEndpoint:
    def endpoints_loaded(self, endpoints):
        assert endpoints is not None
