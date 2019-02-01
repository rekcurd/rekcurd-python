from . import *

import unittest
import time
from functools import wraps
from unittest.mock import patch, Mock
import grpc_testing
from grpc import StatusCode

from rekcurd.protobuf import rekcurd_pb2
from rekcurd.utils import PredictResult


target_service = rekcurd_pb2.DESCRIPTOR.services_by_name['RekcurdWorker']


def patch_predictor(input_type, output_type):
    """Decorator to mock the predictor.
    Patch the several methods of the Predict class to make a fake predictor.
    """

    _prediction_value_map = {
        Type.STRING: PredictResult('Rekcurd', 1.0, option={}),
        Type.BYTES: PredictResult(b'\x8f\xfa;\xc8a\xa3T%', 1.0, option={}),
        Type.ARRAY_INT: PredictResult([2, 3, 5, 7], [1.0, 1.0, 1.0, 1.0], option={}),
        Type.ARRAY_FLOAT: PredictResult([0.78341155, 0.03166816, 0.92745938], [1.0, 1.0, 1.0], option={}),
        Type.ARRAY_STRING: PredictResult(['Rekcurd', 'is', 'awesome'], [1.0, 1.0, 1.0], option={}),
    }

    def test_method(func):
        @wraps(func)
        def inner_method(*args, **kwargs):
            with patch('test.dummy_app.DummyApp.get_type_input',
                       new=Mock(return_value=input_type)) as _, \
                    patch('test.dummy_app.DummyApp.get_type_output',
                          new=Mock(return_value=output_type)) as _, \
                    patch('test.dummy_app.DummyApp.load_model') as _, \
                    patch('test.dummy_app.DummyApp.predict',
                          new=Mock(return_value=_prediction_value_map[output_type])) as _:
                return func(*args, **kwargs)
        return inner_method
    return test_method


class RekcurdWorkerServicerTest(unittest.TestCase):
    """Tests for RekcurdWorkerServicer."""

    def fake_string_request(self):
        request = rekcurd_pb2.StringInput()
        request.input = 'Rekcurd'
        request.option.val = '{}'
        return request

    def fake_bytes_request(self):
        request = rekcurd_pb2.BytesInput()
        request.input = b'\x9cT\xee\xca\x19\xbb\xa44\xfcS'
        request.option.val = '{}'
        return request

    def fake_arrint_request(self):
        request = rekcurd_pb2.ArrIntInput()
        request.input.extend([218, 81, 2, 215, 28])
        request.option.val = '{}'
        return request

    def fake_arrfloat_request(self):
        request = rekcurd_pb2.ArrFloatInput()
        request.input.extend([0.22861859, 0.90036856, 0.03665003, 0.69281863, 0.23225956])
        request.option.val = '{}'
        return request

    def fake_arrstring_request(self):
        request = rekcurd_pb2.ArrStringInput()
        request.input.extend(['Rekcurd', 'Docker', 'Rekcurd', 'Rekcod'])
        request.option.val = '{}'
        return request

    def assertStringResponse(self, response):
        self.assertIsInstance(response, rekcurd_pb2.StringOutput)

    def assertBytesResponse(self, response):
        self.assertIsInstance(response, rekcurd_pb2.BytesOutput)

    def assertArrIntResponse(self, response):
        self.assertIsInstance(response, rekcurd_pb2.ArrIntOutput)

    def assertArrFloatResponse(self, response):
        self.assertIsInstance(response, rekcurd_pb2.ArrFloatOutput)

    def assertArrStringResponse(self, response):
        self.assertIsInstance(response, rekcurd_pb2.ArrStringOutput)

    def setUp(self):
        self._real_time = grpc_testing.strict_real_time()
        self._fake_time = grpc_testing.strict_fake_time(time.time())
        servicer = rekcurd.rekcurd_worker_servicer.RekcurdWorkerServicer(logger=service_logger, app=app)
        descriptors_to_services = {
            target_service: servicer
        }
        self._real_time_server = grpc_testing.server_from_dictionary(
            descriptors_to_services, self._real_time)
        self._fake_time_server = grpc_testing.server_from_dictionary(
            descriptors_to_services, self._fake_time)

    @patch_predictor(Type.STRING, Type.STRING)
    def test_String_String(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_String_String'], (),
            self.fake_string_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertStringResponse(response)

    @patch_predictor(Type.STRING, Type.STRING)
    def test_metadata(self):
        metadata = [('x-request-id', 'test'), ('dummy', 'dummy')]
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_String_String'], metadata,
            self.fake_string_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertStringResponse(response)

    @patch_predictor(Type.STRING, Type.BYTES)
    def test_String_Bytes(self):
        rpc = self._real_time_server.invoke_unary_stream(
            target_service.methods_by_name['Predict_String_Bytes'], (),
            self.fake_string_request(), None)
        initial_metadata = rpc.initial_metadata()
        trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)

    @patch_predictor(Type.STRING, Type.ARRAY_INT)
    def test_String_ArrInt(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_String_ArrInt'], (),
            self.fake_string_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.STRING, Type.ARRAY_FLOAT)
    def test_String_ArrFloat(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_String_ArrFloat'], (),
            self.fake_string_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.STRING, Type.ARRAY_STRING)
    def test_String_ArrString(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_String_ArrString'], (),
            self.fake_string_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.BYTES, Type.STRING)
    def test_Bytes_String(self):
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['Predict_Bytes_String'], (), None)
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertStringResponse(response)

    @patch_predictor(Type.BYTES, Type.BYTES)
    def test_Bytes_Bytes(self):
        rpc = self._real_time_server.invoke_stream_stream(
            target_service.methods_by_name['Predict_Bytes_Bytes'], (), None)
        rpc.send_request(self.fake_bytes_request())
        initial_metadata = rpc.initial_metadata()
        responses = [
            rpc.take_response(),
        ]
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        responses.extend([
            rpc.take_response(),
            rpc.take_response(),
        ])
        rpc.requests_closed()
        trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        for response in responses:
            self.assertBytesResponse(response)

    @patch_predictor(Type.BYTES, Type.ARRAY_INT)
    def test_Bytes_ArrInt(self):
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['Predict_Bytes_ArrInt'], (), None)
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.BYTES, Type.ARRAY_FLOAT)
    def test_Bytes_ArrFloat(self):
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['Predict_Bytes_ArrFloat'], (), None)
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.BYTES, Type.ARRAY_STRING)
    def test_Bytes_ArrString(self):
        rpc = self._real_time_server.invoke_stream_unary(
            target_service.methods_by_name['Predict_Bytes_ArrString'], (), None)
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.send_request(self.fake_bytes_request())
        rpc.requests_closed()
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.STRING)
    def test_ArrInt_String(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrInt_String'], (),
            self.fake_arrint_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertStringResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.BYTES)
    def test_ArrInt_Bytes(self):
        rpc = self._real_time_server.invoke_unary_stream(
            target_service.methods_by_name['Predict_ArrInt_Bytes'], (),
            self.fake_arrint_request(), None)
        initial_metadata = rpc.initial_metadata()
        trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)

    @patch_predictor(Type.ARRAY_INT, Type.ARRAY_INT)
    def test_ArrInt_ArrInt(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrInt_ArrInt'], (),
            self.fake_arrint_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.ARRAY_FLOAT)
    def test_ArrInt_ArrFloat(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrInt_ArrFloat'], (),
            self.fake_arrint_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.ARRAY_STRING)
    def test_ArrInt_ArrString(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrInt_ArrString'], (),
            self.fake_arrint_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.STRING)
    def test_ArrFloat_String(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrFloat_String'], (),
            self.fake_arrfloat_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertStringResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.BYTES)
    def test_ArrFloat_Bytes(self):
        rpc = self._real_time_server.invoke_unary_stream(
            target_service.methods_by_name['Predict_ArrFloat_Bytes'], (),
            self.fake_arrfloat_request(), None)
        initial_metadata = rpc.initial_metadata()
        trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)

    @patch_predictor(Type.ARRAY_FLOAT, Type.ARRAY_INT)
    def test_ArrFloat_ArrInt(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrFloat_ArrInt'], (),
            self.fake_arrfloat_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.ARRAY_FLOAT)
    def test_ArrFloat_ArrFloat(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrFloat_ArrFloat'], (),
            self.fake_arrfloat_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.ARRAY_STRING)
    def test_ArrFloat_ArrString(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrFloat_ArrString'], (),
            self.fake_arrfloat_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.STRING)
    def test_ArrString_String(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrString_String'], (),
            self.fake_arrstring_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertStringResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.BYTES)
    def test_ArrString_Bytes(self):
        rpc = self._real_time_server.invoke_unary_stream(
            target_service.methods_by_name['Predict_ArrString_Bytes'], (),
            self.fake_arrstring_request(), None)
        initial_metadata = rpc.initial_metadata()
        trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)

    @patch_predictor(Type.ARRAY_STRING, Type.ARRAY_INT)
    def test_ArrString_ArrInt(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrString_ArrInt'], (),
            self.fake_arrstring_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.ARRAY_FLOAT)
    def test_ArrString_ArrFloat(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrString_ArrFloat'], (),
            self.fake_arrstring_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.ARRAY_STRING)
    def test_ArrString_ArrString(self):
        rpc = self._real_time_server.invoke_unary_unary(
            target_service.methods_by_name['Predict_ArrString_ArrString'], (),
            self.fake_arrstring_request(), None)
        initial_metadata = rpc.initial_metadata()
        response, trailing_metadata, code, details = rpc.termination()
        self.assertIs(code, StatusCode.OK)
        self.assertArrStringResponse(response)
