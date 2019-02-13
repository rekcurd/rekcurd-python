import unittest
from unittest.mock import Mock

from rekcurd.utils import RekcurdConfig
from rekcurd.logger import FluentSystemLogger, FluentServiceLogger


class FluentSystemLoggerTest(unittest.TestCase):
    """Tests for FluentSystemLogger.
    """

    def setUp(self):
        self.logger = FluentSystemLogger(config=RekcurdConfig())

    def test_exception(self):
        self.assertIsNone(self.logger.exception("Exception"))

    def test_error(self):
        self.assertIsNone(self.logger.error("Exception"))

    def test_debug(self):
        self.assertIsNone(self.logger.debug("Exception"))

    def test_info(self):
        self.assertIsNone(self.logger.info("Exception"))

    def test_warn(self):
        self.assertIsNone(self.logger.warn("Exception"))


class FluentServiceLoggerTest(unittest.TestCase):
    """Tests for FluentServiceLogger.
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
        self.logger = FluentServiceLogger(config=RekcurdConfig())

    def test_emit(self):
        self.assertIsNone(self.logger.emit(self.request, self.response))

    def test_emit_suppressed(self):
        self.assertIsNone(self.logger.emit(self.request, self.response, suppress_log_inout=True))
