import os
import unittest
from functools import wraps
from unittest.mock import patch, Mock

from drucker.protobuf import drucker_pb2
from drucker.utils import PredictResult
from drucker.logger import JsonServiceLogger, JsonSystemLogger
from drucker.test.dummy_app import DummyApp
import drucker.drucker_worker_servicer


os.environ["DRUCKER_TEST_MODE"] = "True"
os.environ["DRUCKER_SETTINGS_YAML"] = "drucker/test/test-settings.yml"

app = DummyApp()
service_logger = JsonServiceLogger(app.config)
system_logger = JsonSystemLogger(app.config)
Type = drucker.drucker_worker_servicer.DruckerWorkerServicer.Type


class DruckerWorkerTest(unittest.TestCase):
    """DruckerWorkerTest is a base class for testing DruckerWorkerServicer.
    This class create xxxOutput instance and check that the return values have correct type.
    """

    def assertStringResponse(self, response):
        self.assertIsInstance(response, drucker_pb2.StringOutput)

    def assertBytesResponse(self, response):
        for item in response:
            self.assertIsInstance(item, drucker_pb2.BytesOutput)

    def assertArrIntResponse(self, response):
        self.assertIsInstance(response, drucker_pb2.ArrIntOutput)

    def assertArrFloatResponse(self, response):
        self.assertIsInstance(response, drucker_pb2.ArrFloatOutput)

    def assertArrStringResponse(self, response):
        self.assertIsInstance(response, drucker_pb2.ArrStringOutput)


_prediction_value_map = {
    Type.STRING: PredictResult('Drucker', 1.0, option={}),
    Type.BYTES: PredictResult(b'\x8f\xfa;\xc8a\xa3T%', 1.0, option={}),
    Type.ARRAY_INT: PredictResult([2, 3, 5, 7], [1.0, 1.0, 1.0, 1.0], option={}),
    Type.ARRAY_FLOAT: PredictResult([0.78341155, 0.03166816, 0.92745938], [1.0, 1.0, 1.0], option={}),
    Type.ARRAY_STRING: PredictResult(['Drucker', 'is', 'awesome'], [1.0, 1.0, 1.0], option={}),
}


def patch_predictor(input_type, output_type):
    """Decorator to mock the predictor.
    Patch the several methods of the Predict class to make a fake predictor.
    """
    def test_method(func):
        @wraps(func)
        def inner_method(*args, **kwargs):
            with patch('drucker.test.dummy_app.DummyApp.get_type_input',
                       new=Mock(return_value=input_type)) as _, \
                    patch('drucker.test.dummy_app.DummyApp.get_type_output',
                          new=Mock(return_value=output_type)) as _, \
                    patch('drucker.test.dummy_app.DummyApp.load_model') as _, \
                    patch('drucker.test.dummy_app.DummyApp.predict',
                          new=Mock(return_value=_prediction_value_map[output_type])) as _:
                return func(*args, **kwargs)
        return inner_method
    return test_method
