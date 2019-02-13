import unittest
from unittest.mock import Mock

from rekcurd.utils import RekcurdConfig
from rekcurd.logger import JsonSystemLogger, JsonServiceLogger


class JsonSystemLoggerTest(unittest.TestCase):
    """Tests for JsonSystemLogger.
    """

    def setUp(self):
        self.logger = JsonSystemLogger(config=RekcurdConfig())

    def test_exception(self):
        self.assertIsNone(self.logger.exception("Exception"))

    def test_error(self):
        self.assertIsNone(self.logger.error("Error"))

    def test_debug(self):
        self.assertIsNone(self.logger.debug("Debug"))

    def test_info(self):
        self.assertIsNone(self.logger.info("Info"))

    def test_warn(self):
        self.assertIsNone(self.logger.warn("Warn"))


class JsonServiceLoggerTest(unittest.TestCase):
    """Tests for JsonServiceLogger.
    """

    def setUp(self):
        self.request = Mock()
        self.request.input = "input"
        self.request.option = Mock()
        self.request.option.val = "request-option"
        self.response = Mock()
        self.response.output = "output"
        self.response.score = 0.0
        self.response.option = Mock()
        self.response.option.val = "response-option"
        self.logger = JsonServiceLogger(config=RekcurdConfig())

    def test_emit(self):
        self.assertIsNone(self.logger.emit(self.request, self.response))

    def test_emit_suppressed(self):
        self.assertIsNone(self.logger.emit(self.request, self.response, suppress_log_inout=True))
