import pytest  # noqa

# from collector.endpoint import Endpoint, load_from_config


class TestEndpoint:
    def endpoints_loaded(self, endpoints):
        assert endpoints is not None
