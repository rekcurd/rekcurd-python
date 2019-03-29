import unittest

from rekcurd.protobuf import rekcurd_pb2
from rekcurd.utils import RekcurdConfig, ModelModeEnum, EvaluateResultDetail, EvaluateResult, PredictResult
from rekcurd.data_servers import DataServer

from . import patch_predictor


class DataServerTest(unittest.TestCase):
    """Tests for DataServer.
    """

    def setUp(self):
        config = RekcurdConfig("./test/test-settings.yml")
        config.set_configurations(
            model_mode=ModelModeEnum.CEPH_S3.value, ceph_access_key="xxx",
            ceph_secret_key="xxx", ceph_host="127.0.0.1", ceph_port=443,
            ceph_is_secure=True, ceph_bucket_name="xxx")
        self.data_server = DataServer(config)

    @patch_predictor()
    def test_get_model_path(self):
        self.assertEqual(self.data_server.get_model_path(), "rekcurd-model/test/model/default.model")

    @patch_predictor()
    def test_get_model_path(self):
        self.assertEqual(self.data_server.switch_model("test/model/switch.model"), "rekcurd-model/test/model/switch.model")

    def __get_UploadModelRequest(self, path: str):
        yield rekcurd_pb2.UploadModelRequest(path=path, data=b'data')

    @patch_predictor()
    def test_upload_model(self):
        request_iterator = self.__get_UploadModelRequest('my_path')
        self.assertEqual(self.data_server.upload_model(request_iterator), 'rekcurd-model/test/model/my_path')

    @patch_predictor()
    def test_upload_model_invalid_path(self):
        request_iterator = self.__get_UploadModelRequest('../my_path')
        with self.assertRaises(Exception):
            self.data_server.upload_model(request_iterator)

    @patch_predictor()
    def test_get_evaluation_data_path(self):
        self.assertEqual(self.data_server.get_evaluation_data_path("test/eval/data"), "rekcurd-eval/data")

    @patch_predictor()
    def test_get_eval_result_detail(self):
        self.assertEqual(self.data_server.get_eval_result_detail("test/eval/detail.pkl"), "rekcurd-eval/detail.pkl")

    def __get_UploadEvaluationDataRequest(self, data_path: str):
        yield rekcurd_pb2.UploadEvaluationDataRequest(data_path=data_path, data=b'data')

    @patch_predictor()
    def test_upload_evaluation_data(self):
        request_iterator = self.__get_UploadEvaluationDataRequest('my_path')
        self.assertEqual(self.data_server.upload_evaluation_data(request_iterator), "rekcurd-eval/my_path")

    @patch_predictor()
    def test_upload_evaluation_data_invalid_path(self):
        request_iterator = self.__get_UploadEvaluationDataRequest('../my_path')
        with self.assertRaises(Exception):
            self.data_server.upload_evaluation_data(request_iterator)

    @patch_predictor()
    def test_upload_evaluation_result(self):
        eval_res = EvaluateResult(1, 0.4, [0.5], [0.5], [0.5], [0.5], ['label'])

        def generate_eval():
            for _ in range(2):
                yield EvaluateResultDetail(result=PredictResult('label', 0.5),
                                           is_correct=True)
            return eval_res
        self.assertEqual(self.data_server.upload_evaluation_result(generate_eval(), "test/eval/data"), eval_res)

    @patch_predictor()
    def test_upload_evaluation_result_invalid_path(self):
        with self.assertRaises(Exception):
            self.data_server.upload_evaluation_result_summary(b'hoge', "test/../data")
