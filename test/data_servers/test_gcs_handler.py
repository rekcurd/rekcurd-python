import unittest

from rekcurd.utils import RekcurdConfig, ModelModeEnum
from rekcurd.data_servers import GcsHandler

from . import patch_predictor


class GcsHandlerTest(unittest.TestCase):
    """Tests for GcsHandlerTest.
    """

    def setUp(self):
        config = RekcurdConfig("./test/test-settings.yml")
        config.set_configurations(
            model_mode=ModelModeEnum.GCS.value, gcs_access_key="xxx",
            gcs_secret_key="xxx", gcs_bucket_name="xxx")
        self.handler = GcsHandler(config)

    @patch_predictor()
    def test_download(self):
        self.assertIsNone(self.handler.download("remote","local"))

    @patch_predictor()
    def test_upload(self):
        self.assertIsNone(self.handler.upload("remote","local"))
