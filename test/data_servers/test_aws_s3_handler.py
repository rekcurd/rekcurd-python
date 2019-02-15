import unittest

from rekcurd.utils import RekcurdConfig, ModelModeEnum
from rekcurd.data_servers import AwsS3Handler

from . import patch_predictor


class AwsS3HandlerTest(unittest.TestCase):
    """Tests for AwsS3HandlerTest.
    """

    def setUp(self):
        config = RekcurdConfig("./test/test-settings.yml")
        config.set_configurations(
            model_mode=ModelModeEnum.AWS_S3.value, aws_access_key="xxx",
            aws_secret_key="xxx", aws_bucket_name="xxx")
        self.handler = AwsS3Handler(config)

    @patch_predictor()
    def test_download(self):
        self.assertIsNone(self.handler.download("remote","local"))

    @patch_predictor()
    def test_upload(self):
        self.assertIsNone(self.handler.upload("remote","local"))
