import unittest
import sys
import time
from functools import wraps
from unittest.mock import patch, Mock, mock_open
import grpc_testing
from grpc import StatusCode

from rekcurd.protobuf import rekcurd_pb2
from rekcurd.rekcurd_dashboard_servicer import RekcurdDashboardServicer
from rekcurd.utils import EvaluateResult, EvaluateResultDetail, PredictResult, EvaluateDetail
from . import app, system_logger


target_service = rekcurd_pb2.DESCRIPTOR.services_by_name['RekcurdDashboard']
eval_result = EvaluateResult(1, 0.8, [0.7], [0.6], [0.5], {'dummy': 0.4})
eval_result_details = [EvaluateResultDetail(PredictResult('pre_label', 0.9), False)]
eval_detail = EvaluateDetail('input', 'label', eval_result_details[0])

# Overwrite CHUNK_SIZE and BYTE_LIMIT to smaller values for testing
chunk_size = 3
RekcurdDashboardServicer.CHUNK_SIZE = chunk_size
# response byte size will be greater than BYTE_LIMIT in 2nd loop
RekcurdDashboardServicer.BYTE_LIMIT = 190


def patch_predictor():
    """Decorator to mock for dashboard.
    """

    def test_method(func):
        @wraps(func)
        def inner_method(*args, **kwargs):
            with patch('rekcurd.rekcurd_dashboard_servicer.uuid.uuid4',
                new=Mock(return_value=Mock(hex='my_uuid'))) as _, \
                    patch('rekcurd.rekcurd_dashboard_servicer.shutil.move',
                        new=Mock(return_value=True)) as _, \
                    patch('rekcurd.rekcurd_dashboard_servicer.Path',
                        new=Mock(return_value=Mock())) as mock_path, \
                    patch('rekcurd.rekcurd_dashboard_servicer.pickle',
                          new=Mock()) as _, \
                    patch('rekcurd.rekcurd_dashboard_servicer.pickle.load',
                          new=Mock(return_value=eval_result)) as _, \
                    patch('builtins.open', new_callable=mock_open) as _:
                mock_path.return_value.name = 'my_path'
                return func(*args, **kwargs)
        return inner_method
    return test_method


class RekcurdWorkerServicerTest(unittest.TestCase):
    """Tests for RekcurdDashboardServicer.
    """

    def setUp(self):
        app.get_model_path = Mock(return_value='test/my_path')
        app.get_eval_path = Mock(return_value='test/my_eval_path')
        app.config.SERVICE_INFRA = 'default'
        app.evaluate = Mock(return_value=(eval_result, eval_result_details))
        self._real_time = grpc_testing.strict_real_time()
        self._fake_time = grpc_testing.strict_fake_time(time.time())
        servicer = RekcurdDashboardServicer(logger=system_logger, app=app)
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
            rekcurd_pb2.ServiceInfoRequest(), None)
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertEqual(response.application_name, 'test')
        self.assertEqual(response.service_name, 'test-001')
        self.assertEqual(response.service_level, 'development')

    @patch_predictor()
    def test_UploadModel(self):
        request = rekcurd_pb2.UploadModelRequest(path='my_path', data=b'data')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['UploadModel'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertEqual(response.status, 1)

    @patch_predictor()
    def test_InvalidUploadModel(self):
        request = rekcurd_pb2.UploadModelRequest(path='../../../my_path', data=b'data')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['UploadModel'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.UNKNOWN)
        self.assertEqual(response.status, 0)

    @patch_predictor()
    def test_SwitchModel(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['SwitchModel'], (),
            rekcurd_pb2.SwitchModelRequest(path='my_path'), None)
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertEqual(response.status, 1)

    @patch_predictor()
    def test_InvalidSwitchModel(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['SwitchModel'], (),
            rekcurd_pb2.SwitchModelRequest(path='../../my_path'), None)
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.UNKNOWN)
        self.assertEqual(response.status, 0)

    @patch_predictor()
    def test_UploadEvaluationData(self):
        request = rekcurd_pb2.UploadEvaluationDataRequest(data_path='my_path', data=b'data_')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['UploadEvaluationData'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertEqual(response.status, 1)

    @patch_predictor()
    def test_InvalidEvaluationData(self):
        request = rekcurd_pb2.UploadEvaluationDataRequest(data_path='../../my_path', data=b'data_')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['UploadEvaluationData'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertEqual(response.status, 0)

    @patch_predictor()
    def test_EvalauteModel(self):
        request = rekcurd_pb2.EvaluateModelRequest(data_path='my_path', result_path='my_path')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['EvaluateModel'], (), None)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.send_request(request)
        rpc.requests_closed()
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
        request = rekcurd_pb2.EvaluateModelRequest(data_path='../../my_path', result_path='my_res_path')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['EvaluateModel'], (), None)
        rpc.send_request(request)
        rpc.requests_closed()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.UNKNOWN)
        self.assertEqual(response.metrics.num, 0)

        request = rekcurd_pb2.EvaluateModelRequest(data_path='my_path', result_path='../my_res_path')
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['EvaluateModel'], (), None)
        rpc.send_request(request)
        rpc.requests_closed()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.UNKNOWN)
        self.assertEqual(response.metrics.num, 0)

    def __send_eval_result(self, size, take_times):
        app.get_evaluate_detail = Mock(return_value=iter(eval_detail for _ in range(size)))
        rpc = self._real_time_server.invoke_unary_stream(
            target_service.methods_by_name['EvaluationResult'], (),
            rekcurd_pb2.EvaluationResultRequest(data_path='my_path', result_path='my_path'), None)
        responses = [rpc.take_response() for _ in range(take_times)]
        return rpc, responses

    @patch_predictor()
    def test_EvalautionResult(self):
        rpc, responses = self.__send_eval_result(1, 1)
        response = responses[0]

        self.assertEqual(round(response.metrics.num, 3), eval_result.num)
        self.assertEqual(round(response.metrics.accuracy, 3), eval_result.accuracy)
        self.assertEqual([round(p, 3) for p in response.metrics.precision], eval_result.precision)
        self.assertEqual([round(r, 3) for r in response.metrics.recall], eval_result.recall)
        self.assertEqual([round(f, 3) for f in response.metrics.fvalue], eval_result.fvalue)
        self.assertEqual(round(response.metrics.option['dummy'], 3), eval_result.option['dummy'])

        self.assertEqual(len(response.detail), 1)
        detail = response.detail[0]
        self.assertEqual(detail.input.str.val, [eval_detail.input])
        self.assertEqual(detail.label.str.val, [eval_detail.label])
        self.assertEqual(detail.output.str.val, [eval_result_details[0].result.label])
        self.assertEqual([round(s, 3) for s in detail.score], [eval_result_details[0].result.score])
        self.assertEqual(detail.is_correct, eval_result_details[0].is_correct)

        with self.assertRaises(ValueError):
            rpc.take_response()

        trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)

    @patch_predictor()
    def test_EvalautionResult_multi_response(self):
        # chunk_size * 3
        rpc, responses = self.__send_eval_result(chunk_size * 3, 3)
        for r in responses:
            self.assertEqual(len(r.detail), chunk_size)
        with self.assertRaises(ValueError):
            rpc.take_response()
        rpc.termination()

        # chunk_size * 2 + 1
        rpc, responses = self.__send_eval_result(chunk_size * 2 + 1, 2)
        self.assertEqual(len(responses[0].detail), chunk_size)
        self.assertEqual(len(responses[1].detail), chunk_size + 1)
        with self.assertRaises(ValueError):
            rpc.take_response()
        rpc.termination()

    def test_get_io_by_type(self):
        servicer = RekcurdDashboardServicer(logger=system_logger, app=app)
        self.assertEqual(servicer.get_io_by_type('test').str.val, ['test'])
        self.assertEqual(servicer.get_io_by_type(['test', 'test2']).str.val, ['test', 'test2'])
        self.assertEqual(servicer.get_io_by_type(2).tensor.val, [2])
        self.assertEqual(servicer.get_io_by_type([2, 3]).tensor.val, [2, 3])

    def test_get_score_by_type(self):
        servicer = RekcurdDashboardServicer(logger=system_logger, app=app)
        score = 4.5
        self.assertEqual(servicer.get_score_by_type(score), [score])
        self.assertEqual(servicer.get_score_by_type([score]), [score])
