import unittest
from functools import wraps
from unittest.mock import Mock, patch

from rekcurd.data_servers import DataServer
from rekcurd.logger import JsonSystemLogger, JsonServiceLogger
from . import app, Type


def patch_predictor():
    """Decorator to mock for dashboard.
    """

    def test_method(func):
        @wraps(func)
        def inner_method(*args, **kwargs):
            with patch('rekcurd.data_servers.LocalHandler.download',
                       new=Mock(return_value=True)) as _, \
                    patch('rekcurd.data_servers.LocalHandler.upload',
                          new=Mock(return_value=True)) as _, \
                    patch('rekcurd.data_servers.CephHandler.download',
                          new=Mock(return_value=True)) as _, \
                    patch('rekcurd.data_servers.CephHandler.upload',
                          new=Mock(return_value=True)) as _:
                return func(*args, **kwargs)
        return inner_method
    return test_method


class RekcurdWorkerTest(unittest.TestCase):
    """Tests for Rekcurd.
    """

    def setUp(self):
        import os
        os.environ["REKCURD_UNITTEST"] = "True"
        app.load_config_file("./test/test-settings.yml")
        app.data_server = DataServer(app.config)
        app.system_logger = JsonSystemLogger(config=app.config)
        app.service_logger = JsonServiceLogger(config=app.config)

    @patch_predictor()
    def test_run(self):
        self.assertIsNone(app.run())

    def test_type(self):
        # TODO: DEPRECATED
        self.assertIsNone(app.set_type(Type.STRING, Type.ARRAY_INT))
        self.assertEqual(app.get_type_input(), Type.STRING)
        self.assertEqual(app.get_type_output(), Type.ARRAY_INT)
