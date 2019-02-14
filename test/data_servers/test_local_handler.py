import unittest

from rekcurd.utils import RekcurdConfig
from rekcurd.data_servers import LocalHandler

from . import patch_predictor


class LocalHandlerTest(unittest.TestCase):
    """Tests for LocalHandler.
    """

    def setUp(self):
        config = RekcurdConfig("./test/test-settings.yml")
        self.handler = LocalHandler(config)

    @patch_predictor()
    def test_download(self):
        with self.assertRaises(Exception):
            self.handler.download("remote","local")

    @patch_predictor()
    def test_upload(self):
        self.assertIsNone(self.handler.upload("remote","local"))
