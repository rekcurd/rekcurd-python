import unittest

from rekcurd.utils import RekcurdConfig, ModelModeEnum
from rekcurd.data_servers import CephHandler

from . import patch_predictor


class CephHandlerTest(unittest.TestCase):
    """Tests for CephHandlerTest.
    """

    def setUp(self):
        config = RekcurdConfig("./test/test-settings.yml")
        config.set_configurations(
            model_mode=ModelModeEnum.CEPH_S3.value, ceph_access_key="xxx",
            ceph_secret_key="xxx", ceph_host="127.0.0.1", ceph_port=443,
            ceph_is_secure=True, ceph_bucket_name="xxx")
        self.handler = CephHandler(config)

    @patch_predictor()
    def test_download(self):
        self.assertIsNone(self.handler.download("remote","local"))

    @patch_predictor()
    def test_upload(self):
        self.assertIsNone(self.handler.upload("remote","local"))
