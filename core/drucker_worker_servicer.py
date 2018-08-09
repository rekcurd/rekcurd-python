#!/usr/bin/python
# -*- coding: utf-8 -*-

import drucker_pb2
import drucker_pb2_grpc

import json

from enum import Enum
from grpc._server import _Context
from typing import Iterator, Union

from logger.logger_interface import ServiceLoggerInterface
from core.predict_interface import PredictResult, PredictInterface


DruckerInput = Union[
    drucker_pb2.StringInput, drucker_pb2.BytesInput,
    drucker_pb2.ArrIntInput, drucker_pb2.ArrFloatInput, drucker_pb2.ArrStringInput]
DruckerOutput = Union[
    drucker_pb2.StringOutput, drucker_pb2.BytesOutput,
    drucker_pb2.ArrIntOutput, drucker_pb2.ArrFloatOutput, drucker_pb2.ArrStringOutput]


dict_any_type_url = {
    'type.googleapis.com/%s'%drucker_pb2.SingleInt32().DESCRIPTOR.full_name: (drucker_pb2.SingleInt32(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleInt64().DESCRIPTOR.full_name: (drucker_pb2.SingleInt64(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleUint32().DESCRIPTOR.full_name: (drucker_pb2.SingleUint32(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleUint64().DESCRIPTOR.full_name: (drucker_pb2.SingleUint64(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleSint32().DESCRIPTOR.full_name: (drucker_pb2.SingleSint32(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleSint64().DESCRIPTOR.full_name: (drucker_pb2.SingleSint64(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleFixed32().DESCRIPTOR.full_name: (drucker_pb2.SingleFixed32(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleFixed64().DESCRIPTOR.full_name: (drucker_pb2.SingleFixed64(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleSfixed32().DESCRIPTOR.full_name: (drucker_pb2.SingleSfixed32(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleSfixed64().DESCRIPTOR.full_name: (drucker_pb2.SingleSfixed64(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleFloat().DESCRIPTOR.full_name: (drucker_pb2.SingleFloat(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleDouble().DESCRIPTOR.full_name: (drucker_pb2.SingleDouble(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleBool().DESCRIPTOR.full_name: (drucker_pb2.SingleBool(), True),
    'type.googleapis.com/%s'%drucker_pb2.SingleString().DESCRIPTOR.full_name: (drucker_pb2.SingleString(), True),
    'type.googleapis.com/%s'%drucker_pb2.ArrInt32().DESCRIPTOR.full_name: (drucker_pb2.ArrInt32(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrInt64().DESCRIPTOR.full_name: (drucker_pb2.ArrInt64(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrUint32().DESCRIPTOR.full_name: (drucker_pb2.ArrUint32(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrUint64().DESCRIPTOR.full_name: (drucker_pb2.ArrUint64(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrSint32().DESCRIPTOR.full_name: (drucker_pb2.ArrSint32(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrSint64().DESCRIPTOR.full_name: (drucker_pb2.ArrSint64(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrFixed32().DESCRIPTOR.full_name: (drucker_pb2.ArrFixed32(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrFixed64().DESCRIPTOR.full_name: (drucker_pb2.ArrFixed64(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrSfixed32().DESCRIPTOR.full_name: (drucker_pb2.ArrSfixed32(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrSfixed64().DESCRIPTOR.full_name: (drucker_pb2.ArrSfixed64(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrFloat().DESCRIPTOR.full_name: (drucker_pb2.ArrFloat(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrDouble().DESCRIPTOR.full_name: (drucker_pb2.ArrDouble(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrBool().DESCRIPTOR.full_name: (drucker_pb2.ArrBool(), False),
    'type.googleapis.com/%s'%drucker_pb2.ArrString().DESCRIPTOR.full_name: (drucker_pb2.ArrString(), False),
}

class DruckerWorkerServicer(drucker_pb2_grpc.DruckerWorkerServicer):
    def __init__(self, logger: ServiceLoggerInterface, predictor: PredictInterface):
        self.logger = logger
        self.predictor = predictor

    def __pack_any_response(self, result:PredictResult):
        response = drucker_pb2.AnyOutput()
        if isinstance(result.label, list):
            chk = result.label[0]
            if isinstance(chk, str):
                output_message = drucker_pb2.ArrString()
            elif isinstance(chk, int):
                output_message = drucker_pb2.ArrInt64()
            elif isinstance(chk, float):
                output_message = drucker_pb2.ArrFloat()
            elif isinstance(chk, bool):
                output_message = drucker_pb2.ArrBool()
            else:
                output_message = None
            output_message.val.extend(result.label)
            response.output.Pack(output_message)
            response.score.extend(result.score)
            response.option.val = result.option
        else:
            chk = result.label
            if isinstance(chk, str):
                output_message = drucker_pb2.SingleString()
            elif isinstance(chk, int):
                output_message = drucker_pb2.SingleInt64()
            elif isinstance(chk, float):
                output_message = drucker_pb2.SingleFloat()
            elif isinstance(chk, bool):
                output_message = drucker_pb2.SingleBool()
            else:
                output_message = None
            output_message.val = result.label
            response.output.Pack(output_message)
            response.score.extend(result.score)
            response.option.val = result.option
        return response

    def Predict_Any_Any(self,
                        request: drucker_pb2.AnyInput,
                        context: _Context
                        ) -> drucker_pb2.AnyOutput:
        ioption = json.loads(request.option.val)
        try:
            input_message, is_single = \
                dict_any_type_url.get(request.input.type_url, None)
            request.input.Unpack(input_message)
            input = input_message.val if is_single else list(input_message.val)
            result = self.predictor.predict(input, ioption)
            response = self.__pack_any_response(result)
        except:
            response = drucker_pb2.AnyOutput()
        self.logger.emit((input,ioption),
                         (result.label,result.score,result.option),
                         ioption.get('suppress_log_inout', False))
        return response

    def Predict_Any_File(self,
                         request: drucker_pb2.AnyInput,
                         context: _Context
                         ) -> drucker_pb2.BytesOutput:
        """TODO: Implement
        """
        ioption = json.loads(request.option.val)
        try:
            input_message, is_single = \
                dict_any_type_url.get(request.input.type_url, None)
            request.input.Unpack(input_message)
            input = input_message.val if is_single else list(input_message.val)
            result = self.predictor.predict(input, ioption)
            response = drucker_pb2.BytesOutput()
            response.output = result.label
            response.score = result.score
            response.option.val = result.option
        except:
            response = drucker_pb2.BytesOutput()
        self.logger.emit((input,ioption),
                         (result.label,result.score,result.option),
                         ioption.get('suppress_log_inout', False))
        yield response

    def Predict_File_Any(self,
                         request_iterator: Iterator[drucker_pb2.BytesInput],
                         context: _Context
                         ) -> drucker_pb2.AnyOutput:
        """TODO: Implement
        """
        for request in request_iterator:
            input = request.input
            ioption = json.loads(request.option.val)
            result = self.predictor.predict(input, ioption)
            response = self.__pack_any_response(result)
            self.logger.emit((input,ioption),
                             (result.label,result.score,result.option),
                             ioption.get('suppress_log_inout', False))
            return response

    def Predict_File_File(self,
                          request_iterator: Iterator[drucker_pb2.BytesInput],
                          context: _Context
                          ) -> drucker_pb2.BytesOutput:
        """TODO: Implement
        """
        for request in request_iterator:
            input = request.input
            ioption = json.loads(request.option.val)
            result = self.predictor.predict(input, ioption)
            response = drucker_pb2.BytesOutput()
            response.output = result.label
            response.score = result.score
            response.option.val = result.option
            self.logger.emit((input,ioption),
                             (result.label,result.score,result.option),
                             ioption.get('suppress_log_inout', False))
            yield response

    class Type(Enum):
        """@deprecated
        """
        STRING = 1
        BYTES = 2
        ARRAY_INT = 3
        ARRAY_FLOAT = 4
        ARRAY_STRING = 5

    def Process(self,
                request: DruckerInput,
                response: DruckerOutput
                ) -> DruckerOutput:
        """@deprecated
        """
        input = request.input
        try:
            ioption = json.loads(request.option.val)
        except:
            ioption = {request.option.val: request.option.val}

        single_output = self.predictor.get_type_output() in [self.Type.STRING, self.Type.BYTES]
        try:
            if not isinstance(input, (str, bytes)):
                input = list(input)
            result = self.predictor.predict(input, ioption)
        except:
            if single_output:
                if isinstance(response, drucker_pb2.StringOutput):
                    label = "None"
                elif isinstance(response, drucker_pb2.BytesOutput):
                    label = b'None'
                else:
                    label = None
                result = PredictResult(label=label, score=0.0, option={})
            else:
                if isinstance(response, drucker_pb2.ArrStringOutput):
                    label = ["None"]
                elif isinstance(response, drucker_pb2.ArrIntOutput):
                    label = [0]
                elif isinstance(response, drucker_pb2.ArrFloatOutput):
                    label = [0.0]
                else:
                    label = None
                result = PredictResult(label=label, score=[0.0], option={})
        if single_output:
            response.output = result.label
            response.score = result.score
        else:
            response.output.extend(result.label)
            response.score.extend(result.score)
        response.option.val = result.option
        self.logger.emit((input,ioption),
                         (result.label,result.score,result.option),
                         ioption.get('suppress_log_inout', False))
        return response

    def Predict_String_String(self,
                              request: drucker_pb2.StringInput,
                              context: _Context
                              ) -> drucker_pb2.StringOutput:
        """@deprecated
        """
        response = drucker_pb2.StringOutput()
        self.predictor.set_type(self.Type.STRING, self.Type.STRING)
        return self.Process(request, response)

    def Predict_String_Bytes(self,
                             request: drucker_pb2.StringInput,
                             context: _Context
                             ) -> drucker_pb2.BytesOutput:
        """@deprecated
        """
        response = drucker_pb2.BytesOutput()
        self.predictor.set_type(self.Type.STRING, self.Type.BYTES)
        yield self.Process(request, response)

    def Predict_String_ArrInt(self,
                              request: drucker_pb2.StringInput,
                              context: _Context
                              ) -> drucker_pb2.ArrIntOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrIntOutput()
        self.predictor.set_type(self.Type.STRING, self.Type.ARRAY_INT)
        return self.Process(request, response)

    def Predict_String_ArrFloat(self,
                                request: drucker_pb2.StringInput,
                                context: _Context
                                ) -> drucker_pb2.ArrFloatOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrFloatOutput()
        self.predictor.set_type(self.Type.STRING, self.Type.ARRAY_FLOAT)
        return self.Process(request, response)

    def Predict_String_ArrString(self,
                                 request: drucker_pb2.StringInput,
                                 context: _Context
                                 ) -> drucker_pb2.ArrStringOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrStringOutput()
        self.predictor.set_type(self.Type.STRING, self.Type.ARRAY_STRING)
        return self.Process(request, response)

    def Predict_Bytes_String(self,
                             request_iterator: Iterator[drucker_pb2.BytesInput],
                             context: _Context
                             ) -> drucker_pb2.StringOutput:
        """@deprecated
        """
        for request in request_iterator:
            response = drucker_pb2.StringOutput()
            self.predictor.set_type(self.Type.BYTES, self.Type.STRING)
            return self.Process(request, response)

    def Predict_Bytes_Bytes(self,
                            request_iterator: Iterator[drucker_pb2.BytesInput],
                            context: _Context
                            ) -> drucker_pb2.BytesOutput:
        """@deprecated
        """
        for request in request_iterator:
            response = drucker_pb2.BytesOutput()
            self.predictor.set_type(self.Type.BYTES, self.Type.BYTES)
            yield self.Process(request, response)

    def Predict_Bytes_ArrInt(self,
                             request_iterator: Iterator[drucker_pb2.BytesInput],
                             context: _Context
                             ) -> drucker_pb2.ArrIntOutput:
        """@deprecated
        """
        for request in request_iterator:
            response = drucker_pb2.ArrIntOutput()
            self.predictor.set_type(self.Type.BYTES, self.Type.ARRAY_INT)
            return self.Process(request, response)

    def Predict_Bytes_ArrFloat(self,
                               request_iterator: Iterator[drucker_pb2.BytesInput],
                               context: _Context
                               ) -> drucker_pb2.ArrFloatOutput:
        """@deprecated
        """
        for request in request_iterator:
            response = drucker_pb2.ArrFloatOutput()
            self.predictor.set_type(self.Type.BYTES, self.Type.ARRAY_FLOAT)
            return self.Process(request, response)

    def Predict_Bytes_ArrString(self,
                                request_iterator: Iterator[drucker_pb2.BytesInput],
                                context: _Context
                                ) -> drucker_pb2.ArrStringOutput:
        """@deprecated
        """
        for request in request_iterator:
            response = drucker_pb2.ArrStringOutput()
            self.predictor.set_type(self.Type.BYTES, self.Type.ARRAY_STRING)
            return self.Process(request, response)

    def Predict_ArrInt_String(self,
                              request: drucker_pb2.ArrIntInput,
                              context: _Context
                              ) -> drucker_pb2.StringOutput:
        """@deprecated
        """
        response = drucker_pb2.StringOutput()
        self.predictor.set_type(self.Type.ARRAY_INT, self.Type.STRING)
        return self.Process(request, response)

    def Predict_ArrInt_Bytes(self,
                             request: drucker_pb2.ArrIntInput,
                             context: _Context
                             ) -> drucker_pb2.BytesOutput:
        """@deprecated
        """
        response = drucker_pb2.BytesOutput()
        self.predictor.set_type(self.Type.ARRAY_INT, self.Type.BYTES)
        yield self.Process(request, response)

    def Predict_ArrInt_ArrInt(self,
                              request: drucker_pb2.ArrIntInput,
                              context: _Context
                              ) -> drucker_pb2.ArrIntOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrIntOutput()
        self.predictor.set_type(self.Type.ARRAY_INT, self.Type.ARRAY_INT)
        return self.Process(request, response)

    def Predict_ArrInt_ArrFloat(self,
                                request: drucker_pb2.ArrIntInput,
                                context: _Context
                                ) -> drucker_pb2.ArrFloatOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrFloatOutput()
        self.predictor.set_type(self.Type.ARRAY_INT, self.Type.ARRAY_FLOAT)
        return self.Process(request, response)

    def Predict_ArrInt_ArrString(self,
                                 request: drucker_pb2.ArrIntInput,
                                 context: _Context
                                 ) -> drucker_pb2.ArrStringOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrStringOutput()
        self.predictor.set_type(self.Type.ARRAY_INT, self.Type.ARRAY_STRING)
        return self.Process(request, response)

    def Predict_ArrFloat_String(self,
                                request: drucker_pb2.ArrFloatInput,
                                context: _Context
                                ) -> drucker_pb2.StringOutput:
        """@deprecated
        """
        response = drucker_pb2.StringOutput()
        self.predictor.set_type(self.Type.ARRAY_FLOAT, self.Type.STRING)
        return self.Process(request, response)

    def Predict_ArrFloat_Bytes(self,
                               request: drucker_pb2.ArrFloatInput,
                               context: _Context
                               ) -> drucker_pb2.BytesOutput:
        """@deprecated
        """
        response = drucker_pb2.BytesOutput()
        self.predictor.set_type(self.Type.ARRAY_FLOAT, self.Type.BYTES)
        yield self.Process(request, response)

    def Predict_ArrFloat_ArrInt(self,
                                request: drucker_pb2.ArrFloatInput,
                                context: _Context
                                ) -> drucker_pb2.ArrIntOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrIntOutput()
        self.predictor.set_type(self.Type.ARRAY_FLOAT, self.Type.ARRAY_INT)
        return self.Process(request, response)

    def Predict_ArrFloat_ArrFloat(self,
                                  request: drucker_pb2.ArrFloatInput,
                                  context: _Context
                                  ) -> drucker_pb2.ArrFloatOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrFloatOutput()
        self.predictor.set_type(self.Type.ARRAY_FLOAT, self.Type.ARRAY_FLOAT)
        return self.Process(request, response)

    def Predict_ArrFloat_ArrString(self,
                                   request: drucker_pb2.ArrFloatInput,
                                   context: _Context
                                   ) -> drucker_pb2.ArrStringOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrStringOutput()
        self.predictor.set_type(self.Type.ARRAY_FLOAT, self.Type.ARRAY_STRING)
        return self.Process(request, response)

    def Predict_ArrString_String(self,
                                 request: drucker_pb2.ArrStringInput,
                                 context: _Context
                                 ) -> drucker_pb2.StringOutput:
        """@deprecated
        """
        response = drucker_pb2.StringOutput()
        self.predictor.set_type(self.Type.ARRAY_STRING, self.Type.STRING)
        return self.Process(request, response)

    def Predict_ArrString_Bytes(self,
                                request: drucker_pb2.ArrStringInput,
                                context: _Context
                                ) -> drucker_pb2.BytesOutput:
        """@deprecated
        """
        response = drucker_pb2.BytesOutput()
        self.predictor.set_type(self.Type.ARRAY_STRING, self.Type.BYTES)
        yield self.Process(request, response)

    def Predict_ArrString_ArrInt(self,
                                 request: drucker_pb2.ArrStringInput,
                                 context: _Context
                                 ) -> drucker_pb2.ArrIntOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrIntOutput()
        self.predictor.set_type(self.Type.ARRAY_STRING, self.Type.ARRAY_INT)
        return self.Process(request, response)

    def Predict_ArrString_ArrFloat(self,
                                   request: drucker_pb2.ArrStringInput,
                                   context: _Context
                                   ) -> drucker_pb2.ArrFloatOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrFloatOutput()
        self.predictor.set_type(self.Type.ARRAY_STRING, self.Type.ARRAY_FLOAT)
        return self.Process(request, response)

    def Predict_ArrString_ArrString(self,
                                    request: drucker_pb2.ArrStringInput,
                                    context: _Context
                                    ) -> drucker_pb2.ArrStringOutput:
        """@deprecated
        """
        response = drucker_pb2.ArrStringOutput()
        self.predictor.set_type(self.Type.ARRAY_STRING, self.Type.ARRAY_STRING)
        return self.Process(request, response)
