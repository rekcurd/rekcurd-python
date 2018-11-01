from . import *


def _fake_string_request():
    request = drucker_pb2.StringInput()
    request.input = 'Rekcurd'
    request.option.val = '{}'
    return request


def _fake_bytes_request():
    request = drucker_pb2.BytesInput()
    request.input = b'\x9cT\xee\xca\x19\xbb\xa44\xfcS'
    request.option.val = '{}'
    return iter([request])


def _fake_arrint_request():
    request = drucker_pb2.ArrIntInput()
    request.input.extend([218, 81, 2, 215, 28])
    request.option.val = '{}'
    return request


def _fake_arrfloat_request():
    request = drucker_pb2.ArrFloatInput()
    request.input.extend([0.22861859, 0.90036856, 0.03665003, 0.69281863, 0.23225956])
    request.option.val = '{}'
    return request


def _fake_arrstring_request():
    request = drucker_pb2.ArrStringInput()
    request.input.extend(['Drucker', 'Docker', 'Rekcurd', 'Rekcod'])
    request.option.val = '{}'
    return request


class DruckerWorkerServicerTest(DruckerWorkerTest):
    """Tests for DruckerWorkerServicer.
    Initialize a servicer instance with patched predict class.
    Call different methods of the servicer and check whether the return value has correct type.
    """

    @patch_predictor(Type.STRING, Type.STRING)
    def test_String_String(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_string_request()
        response = servicer.Predict_String_String(request=request, context=None)
        self.assertStringResponse(response)

    @patch_predictor(Type.STRING, Type.BYTES)
    def test_String_Bytes(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_string_request()
        response = servicer.Predict_String_Bytes(request=request, context=None)
        self.assertBytesResponse(response)

    @patch_predictor(Type.STRING, Type.ARRAY_INT)
    def test_String_ArrInt(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_string_request()
        response = servicer.Predict_String_ArrInt(request=request, context=None)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.STRING, Type.ARRAY_FLOAT)
    def test_String_ArrFloat(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_string_request()
        response = servicer.Predict_String_ArrFloat(request=request, context=None)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.STRING, Type.ARRAY_STRING)
    def test_String_ArrString(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_string_request()
        response = servicer.Predict_String_ArrString(request=request, context=None)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.BYTES, Type.STRING)
    def test_Bytes_String(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request_iter = _fake_bytes_request()
        response = servicer.Predict_Bytes_String(request_iterator=request_iter, context=None)
        self.assertStringResponse(response)

    @patch_predictor(Type.BYTES, Type.BYTES)
    def test_Bytes_Bytes(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request_iter = _fake_bytes_request()
        response = servicer.Predict_Bytes_Bytes(request_iterator=request_iter, context=None)
        self.assertBytesResponse(response)

    @patch_predictor(Type.BYTES, Type.ARRAY_INT)
    def test_Bytes_ArrInt(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request_iter = _fake_bytes_request()
        response = servicer.Predict_Bytes_ArrInt(request_iterator=request_iter, context=None)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.BYTES, Type.ARRAY_FLOAT)
    def test_Bytes_ArrFloat(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request_iter = _fake_bytes_request()
        response = servicer.Predict_Bytes_ArrFloat(request_iterator=request_iter, context=None)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.BYTES, Type.ARRAY_STRING)
    def test_Bytes_ArrString(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request_iter = _fake_bytes_request()
        response = servicer.Predict_Bytes_ArrString(request_iterator=request_iter, context=None)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.STRING)
    def test_ArrInt_String(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrint_request()
        response = servicer.Predict_ArrInt_String(request=request, context=None)
        self.assertStringResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.BYTES)
    def test_ArrInt_Bytes(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrint_request()
        response = servicer.Predict_ArrInt_Bytes(request=request, context=None)
        self.assertBytesResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.ARRAY_INT)
    def test_ArrInt_ArrInt(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrint_request()
        response = servicer.Predict_ArrInt_ArrInt(request=request, context=None)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.ARRAY_FLOAT)
    def test_ArrInt_ArrFloat(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrint_request()
        response = servicer.Predict_ArrInt_ArrFloat(request=request, context=None)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.ARRAY_INT, Type.ARRAY_STRING)
    def test_ArrInt_ArrString(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrint_request()
        response = servicer.Predict_ArrInt_ArrString(request=request, context=None)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.STRING)
    def test_ArrFloat_String(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrfloat_request()
        response = servicer.Predict_ArrFloat_String(request=request, context=None)
        self.assertStringResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.BYTES)
    def test_ArrFloat_Bytes(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrfloat_request()
        response = servicer.Predict_ArrFloat_Bytes(request=request, context=None)
        self.assertBytesResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.ARRAY_INT)
    def test_ArrFloat_ArrInt(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrfloat_request()
        response = servicer.Predict_ArrFloat_ArrInt(request=request, context=None)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.ARRAY_FLOAT)
    def test_ArrFloat_ArrFloat(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrfloat_request()
        response = servicer.Predict_ArrFloat_ArrFloat(request=request, context=None)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.ARRAY_FLOAT, Type.ARRAY_STRING)
    def test_ArrFloat_ArrString(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrfloat_request()
        response = servicer.Predict_ArrFloat_ArrString(request=request, context=None)
        self.assertArrStringResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.STRING)
    def test_ArrString_String(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrstring_request()
        response = servicer.Predict_ArrString_String(request=request, context=None)
        self.assertStringResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.BYTES)
    def test_ArrString_Bytes(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrstring_request()
        response = servicer.Predict_ArrString_Bytes(request=request, context=None)
        self.assertBytesResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.ARRAY_INT)
    def test_ArrString_ArrInt(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrstring_request()
        response = servicer.Predict_ArrString_ArrInt(request=request, context=None)
        self.assertArrIntResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.ARRAY_FLOAT)
    def test_ArrString_ArrFloat(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrstring_request()
        response = servicer.Predict_ArrString_ArrFloat(request=request, context=None)
        self.assertArrFloatResponse(response)

    @patch_predictor(Type.ARRAY_STRING, Type.ARRAY_STRING)
    def test_ArrString_ArrString(self):
        servicer = drucker.drucker_worker_servicer.DruckerWorkerServicer(logger=service_logger, app=app)
        request = _fake_arrstring_request()
        response = servicer.Predict_ArrString_ArrString(request=request, context=None)
        self.assertArrStringResponse(response)
