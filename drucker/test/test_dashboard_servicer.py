import unittest
import time
from functools import wraps
from unittest.mock import patch, Mock, mock_open, call
import grpc_testing
from grpc import StatusCode

from drucker.protobuf import drucker_pb2
from drucker.drucker_dashboard_servicer import DruckerDashboardServicer
from drucker.utils import EvaluateResult, EvaluateDetail, PredictResult
from . import app, system_logger


target_service = drucker_pb2.DESCRIPTOR.services_by_name['DruckerDashboard']
eval_result = EvaluateResult(1, 0.8, [0.7], [0.6], [0.5], {'dummy': 0.4})
details = [EvaluateDetail('test_input', 'test_label', PredictResult('pre_label', 0.9), False)]


def patch_predictor():
    """Decorator to mock for dashboard.
    """

    def test_method(func):
        @wraps(func)
        def inner_method(*args, **kwargs):
            with patch('drucker.drucker_dashboard_servicer.uuid.uuid4',
                new=Mock(return_value=Mock(hex='my_uuid'))) as _, \
                    patch('drucker.drucker_dashboard_servicer.shutil.move',
                        new=Mock(return_value=True)) as _, \
                    patch('drucker.drucker_dashboard_servicer.Path',
                        new=Mock(return_value=Mock())) as mock_path, \
                    patch('drucker.drucker_dashboard_servicer.pickle',
                          new=Mock()) as _, \
                    patch('builtins.open', new_callable=mock_open) as _:
                mock_path.return_value.name = 'my_path'
                return func(*args, **kwargs)
        return inner_method
    return test_method


class DruckerWorkerServicerTest(unittest.TestCase):
    """Tests for DruckerDashboardServicer.
    """

    def setUp(self):
        app.get_model_path = Mock(return_value='test/my_path')
        app.config.SERVICE_INFRA = 'default'
        app.evaluate = Mock(return_value=(eval_result, details))
        self._real_time = grpc_testing.strict_real_time()
        self._fake_time = grpc_testing.strict_fake_time(time.time())
        servicer = DruckerDashboardServicer(logger=system_logger, app=app)
        descriptors_to_services = {
            target_service: servicer
        }
        self._real_time_server = grpc_testing.server_from_dictionary(
            descriptors_to_services, self._real_time)
        self._fake_time_server = grpc_testing.server_from_dictionary(
            descriptors_to_services, self._fake_time)

    def test_ServiceInfo(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['ServiceInfo'], (),
            drucker_pb2.ServiceInfoRequest(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertEqual(response.application_name, 'test')
        self.assertEqual(response.service_name, 'test-001')
        self.assertEqual(response.service_level, 'development')

    @patch_predictor()
    def test_UploadModel(self):
        request = drucker_pb2.UploadModelRequest(path='my_path', data=b'data')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['UploadModel'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertEqual(response.status, 1)


    @patch_predictor()
    def test_InvalidUploadModel(self):
        request = drucker_pb2.UploadModelRequest(path='../../../my_path', data=b'data')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['UploadModel'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.UNKNOWN)
        self.assertEqual(response.status, 0)

    @patch_predictor()
    def test_SwitchModel(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['SwitchModel'], (),
            drucker_pb2.SwitchModelRequest(path='my_path'), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertEqual(response.status, 1)

    @patch_predictor()
    def test_InvalidSwitchModel(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['SwitchModel'], (),
            drucker_pb2.SwitchModelRequest(path='../../my_path'), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.UNKNOWN)
        self.assertEqual(response.status, 0)

    @patch_predictor()
    def test_EvalauteModel(self):
        request = drucker_pb2.EvaluateModelRequest(data_path='my_path', data=b'data')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['EvaluateModel'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertEqual(round(response.metrics.num, 3), eval_result.num)
        self.assertEqual(round(response.metrics.accuracy, 3), eval_result.accuracy)
        self.assertEqual([round(p, 3) for p in response.metrics.precision], eval_result.precision)
        self.assertEqual([round(r, 3) for r in response.metrics.recall], eval_result.recall)
        self.assertEqual([round(f, 3) for f in response.metrics.fvalue], eval_result.fvalue)
        self.assertEqual(round(response.metrics.option['dummy'], 3), eval_result.option['dummy'])

    @patch_predictor()
    def test_InvalidEvalauteModel(self):
        request = drucker_pb2.EvaluateModelRequest(data_path='../../my_path', data=b'data')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['EvaluateModel'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.UNKNOWN)
        self.assertEqual(response.metrics.num, 0)
