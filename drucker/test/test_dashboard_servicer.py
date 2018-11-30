import unittest
from unittest.mock import patch, Mock, mock_open, call
import grpc

from drucker.protobuf import drucker_pb2
from drucker.drucker_dashboard_servicer import DruckerDashboardServicer
from drucker.utils import EvaluateResult, EvaluateDetail, PredictResult, EvaluateData
from . import app, system_logger


class DruckerWorkerServicerTest(unittest.TestCase):
    """Tests for DruckerDashboardServicer.
    """

    def test_ServiceInfo(self):
        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        request = drucker_pb2.ServiceInfoRequest()
        response = servicer.ServiceInfo(request, Mock())
        self.assertEqual(response.application_name, 'test')
        self.assertEqual(response.service_name, 'test-001')
        self.assertEqual(response.service_level, 'development')

    @patch('drucker.drucker_dashboard_servicer.uuid')
    @patch('drucker.drucker_dashboard_servicer.shutil')
    @patch('drucker.drucker_dashboard_servicer.Path')
    @patch("builtins.open", new_callable=mock_open)
    def test_UploadModel(self, mock_file, mock_path_class, mock_shutil, mock_uuid):
        # mock setting
        mock_path_class.return_value = Mock()
        mock_path_class.return_value.name = 'my_path'
        mock_shutil.move.return_value = True
        mock_uuid.uuid4.return_value = Mock(hex='my_uuid')

        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        requests = iter(drucker_pb2.UploadModelRequest(path='my_path', data=b'data') for _ in range(1, 3))
        response = servicer.UploadModel(requests, Mock())

        tmp_path = './test-model/test/my_uuid'
        save_path = './test-model/test/my_path'

        self.assertEqual(response.status, 1)
        mock_path_class.assert_has_calls([
            call(tmp_path),
            call(save_path)
        ], any_order=True)
        mock_shutil.move.assert_called_once_with(tmp_path, save_path)

    @patch('drucker.drucker_dashboard_servicer.uuid')
    @patch('drucker.drucker_dashboard_servicer.shutil')
    @patch('drucker.drucker_dashboard_servicer.Path')
    @patch("builtins.open", new_callable=mock_open)
    def test_InvalidUploadModel(self, mock_file, mock_path_class, mock_shutil, mock_uuid):
        # mock setting
        mock_path_class.return_value = Mock()
        mock_path_class.return_value.name = 'my_path'
        mock_shutil.move.return_value = True
        mock_uuid.uuid4.return_value = Mock(hex='my_uuid')

        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        requests = iter(drucker_pb2.UploadModelRequest(path='../../../my_path', data=b'data') for _ in range(1, 3))
        response = servicer.UploadModel(requests, Mock())

        self.assertEqual(response.status, 0)

    @patch('drucker.test.DummyApp')
    def test_SwitchModel(self, mock_app):
        # mock setting
        mock_app.get_model_path.return_value = 'test/my_path'
        mock_app.config.SERVICE_INFRA = 'default'

        servicer = DruckerDashboardServicer(logger=system_logger, app=mock_app)
        request = drucker_pb2.SwitchModelRequest(path='my_path')
        response = servicer.SwitchModel(request, Mock())

        self.assertEqual(response.status, 1)
        mock_app.load_model.assert_called_once_with()

    @patch('drucker.test.DummyApp')
    @patch('drucker.drucker_dashboard_servicer.Path')
    def test_InvalidSwitchModel(self, mock_path_class, mock_app):
        # mock setting
        mock_path_class.return_value = Mock()
        mock_path_class.return_value.name = 'my_path'
        mock_app.get_model_path.return_value = 'test/my_path'
        mock_app.config.SERVICE_INFRA = 'default'

        servicer = DruckerDashboardServicer(logger=system_logger, app=mock_app)
        request = drucker_pb2.SwitchModelRequest(path='../../my_path')
        response = servicer.SwitchModel(request, Mock())

        self.assertEqual(response.status, 0)

    def test_UploadEvaluationData(self):
        # mock setting
        mockio = mock_open()
        mock_file = mockio()

        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        requests = iter(drucker_pb2.UploadEvaluationDataRequest(data_path='my_path', data=b'data_') for _ in range(1, 3))
        with patch('drucker.drucker_dashboard_servicer.open', mockio):
            response = servicer.UploadEvaluationData(requests, Mock())
        self.assertEqual(response.status, 1)

        mock_file.write.assert_called_once_with(b'data_data_')
        mockio.assert_called_with("./eval/test/my_path", "wb")

    def test_InvalidEvaluationData(self):
        # mock setting
        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        requests = iter(drucker_pb2.UploadEvaluationDataRequest(data_path='../../my_path', data=b'data_') for _ in range(1, 3))
        response = servicer.UploadEvaluationData(requests, Mock())
        self.assertEqual(response.status, 0)

    @patch("builtins.open", new_callable=mock_open)
    @patch('drucker.drucker_dashboard_servicer.pickle')
    def test_EvalauteModel(self, mock_pickle, mock_file):
        # mock setting
        eval_result = EvaluateResult(1, 0.8, [0.7], [0.6], [0.5], {'dummy': 0.4})
        details = [EvaluateDetail(PredictResult('pre_label', 0.9), False)]
        eval_data = iter([EvaluateData('test_input', 'test_label')])
        app.evaluate = Mock(return_value=(eval_result, details))
        app.parse_eval_data = Mock(return_value=eval_data)

        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        requests = iter(drucker_pb2.EvaluateModelRequest(data_path='my_path', result_path='my_res_path') for _ in range(1, 3))
        response = servicer.EvaluateModel(requests, Mock())

        self.assertEqual(round(response.metrics.num, 3), eval_result.num)
        self.assertEqual(round(response.metrics.accuracy, 3), eval_result.accuracy)
        self.assertEqual([round(p, 3) for p in response.metrics.precision], eval_result.precision)
        self.assertEqual([round(r, 3) for r in response.metrics.recall], eval_result.recall)
        self.assertEqual([round(f, 3) for f in response.metrics.fvalue], eval_result.fvalue)
        self.assertEqual(round(response.metrics.option['dummy'], 3), eval_result.option['dummy'])

        app.parse_eval_data.assert_called_once_with('./eval/test/my_path')
        app.evaluate.assert_called_once_with(eval_data)

        mock_file.assert_has_calls([
            call("./eval/test/my_res_path_eval_res.pkl", "wb"),
            call("./eval/test/my_res_path_eval_detail.pkl", "wb")
        ], any_order=True)

    @patch("builtins.open", new_callable=mock_open)
    @patch('drucker.drucker_dashboard_servicer.pickle')
    @patch('drucker.drucker_dashboard_servicer.Path')
    def test_InvalidEvalauteModel(self, mock_path_class, mock_pickle, mock_file):
        servicer = DruckerDashboardServicer(logger=system_logger, app=app)

        requests = iter(drucker_pb2.EvaluateModelRequest(data_path='../../my_path') for _ in range(1, 3))
        response = servicer.EvaluateModel(requests, Mock())
        self.assertEqual(response.metrics.num, 0)

        requests = iter(drucker_pb2.EvaluateModelRequest(result_path='../../my_path') for _ in range(1, 3))
        response = servicer.EvaluateModel(requests, Mock())
        self.assertEqual(response.metrics.num, 0)

    def test_error_handling(self):
        # mock setting
        app.get_model_path = Mock(side_effect=Exception('dummy exception'))
        mock_context = Mock()

        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        request = drucker_pb2.SwitchModelRequest(path='my_path')
        response = servicer.SwitchModel(request, mock_context)

        self.assertEqual(response.status, 0)
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.UNKNOWN)
        mock_context.set_details.assert_called_once_with('dummy exception')
