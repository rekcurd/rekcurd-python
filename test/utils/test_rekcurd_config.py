import os
import unittest

from rekcurd.utils import RekcurdConfig, ModelModeEnum


class RekcurdConfigTest(unittest.TestCase):
    """Tests for RekcurdConfig.
    """

    def test_load_from_file(self):
        config = RekcurdConfig("./test/test-settings.yml")
        self.assertEqual(config.DEBUG_MODE, True)
        self.assertEqual(config.APPLICATION_NAME, "test")
        self.assertEqual(config.MODEL_MODE_ENUM, ModelModeEnum.LOCAL)

    def test_load_from_env(self):
        os.environ["REKCURD_KUBERNETES_MODE"] = "True"
        os.environ["REKCURD_DEBUG_MODE"] = "False"
        os.environ["REKCURD_APPLICATION_NAME"] = "test2"
        os.environ["REKCURD_MODEL_MODE"] = ModelModeEnum.CEPH_S3.value
        config = RekcurdConfig("./test/test-settings.yml")
        self.assertEqual(config.DEBUG_MODE, False)
        self.assertEqual(config.APPLICATION_NAME, "test2")
        self.assertEqual(config.MODEL_MODE_ENUM, ModelModeEnum.CEPH_S3)
        del os.environ["REKCURD_KUBERNETES_MODE"]
        del os.environ["REKCURD_DEBUG_MODE"]
        del os.environ["REKCURD_APPLICATION_NAME"]
        del os.environ["REKCURD_MODEL_MODE"]

    def test_set_configurations(self):
        config = RekcurdConfig("./test/test-settings.yml")
        config.set_configurations(debug_mode=False, application_name="test3", model_mode=ModelModeEnum.AWS_S3.value)
        self.assertEqual(config.DEBUG_MODE, False)
        self.assertEqual(config.APPLICATION_NAME, "test3")
        self.assertEqual(config.MODEL_MODE_ENUM, ModelModeEnum.AWS_S3)
