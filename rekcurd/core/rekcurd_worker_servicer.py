#!/usr/bin/python
# -*- coding: utf-8 -*-


import json

from enum import Enum
from grpc import ServicerContext
from typing import Iterator, Union

from .rekcurd_worker import RekcurdPack
from rekcurd.utils import PredictResult
from rekcurd.protobuf import rekcurd_pb2, rekcurd_pb2_grpc


RekcurdInput = Union[
    rekcurd_pb2.StringInput, rekcurd_pb2.BytesInput,
    rekcurd_pb2.ArrIntInput, rekcurd_pb2.ArrFloatInput, rekcurd_pb2.ArrStringInput]
RekcurdOutput = Union[
    rekcurd_pb2.StringOutput, rekcurd_pb2.BytesOutput,
    rekcurd_pb2.ArrIntOutput, rekcurd_pb2.ArrFloatOutput, rekcurd_pb2.ArrStringOutput]


class RekcurdWorkerServicer(rekcurd_pb2_grpc.RekcurdWorkerServicer):
    class Type(Enum):
        STRING = 1
        BYTES = 2
        ARRAY_INT = 3
        ARRAY_FLOAT = 4
        ARRAY_STRING = 5

    def __init__(self, rekcurd_pack: RekcurdPack):
        self.rekcurd_pack = rekcurd_pack
        self.system_logger = rekcurd_pack.app.system_logger
        self.service_logger = rekcurd_pack.app.service_logger

    def Process(self,
                request: RekcurdInput,
                context: ServicerContext,
                response: RekcurdOutput
                ) -> RekcurdOutput:

        input = request.input
        try:
            ioption = json.loads(request.option.val)
        except:
            ioption = {request.option.val: request.option.val}

        single_output = self.rekcurd_pack.app.get_type_output() in [self.Type.STRING, self.Type.BYTES]
        try:
            result = self.rekcurd_pack.app.predict(self.rekcurd_pack.predictor, input, ioption)
        except Exception as e:
            self.system_logger.error(str(e))
            if single_output:
                if isinstance(response, rekcurd_pb2.StringOutput):
                    label = "None"
                elif isinstance(response, rekcurd_pb2.BytesOutput):
                    label = b'None'
                else:
                    label = None
                result = PredictResult(label=label, score=0.0, option={})
            else:
                if isinstance(response, rekcurd_pb2.ArrStringOutput):
                    label = ["None"]
                elif isinstance(response, rekcurd_pb2.ArrIntOutput):
                    label = [0]
                elif isinstance(response, rekcurd_pb2.ArrFloatOutput):
                    label = [0.0]
                else:
                    label = None
                result = PredictResult(label=label, score=[0.0], option={})

        try:
            if single_output:
                response.output = result.label
                response.score = result.score
            else:
                response.output.extend(result.label)
                response.score.extend(result.score)
            response.option.val = result.option
        except Exception as e:
            self.system_logger.error(str(e))

        self.service_logger.emit(request, response, ioption.get('suppress_log_inout', False))
        return response

    def Predict_String_String(self,
                              request: rekcurd_pb2.StringInput,
                              context: ServicerContext
                              ) -> rekcurd_pb2.StringOutput:
        response = rekcurd_pb2.StringOutput()
        self.rekcurd_pack.app.set_type(self.Type.STRING, self.Type.STRING)
        return self.Process(request, context, response)

    def Predict_String_Bytes(self,
                             request: rekcurd_pb2.StringInput,
                             context: ServicerContext
                             ) -> rekcurd_pb2.BytesOutput:
        response = rekcurd_pb2.BytesOutput()
        self.rekcurd_pack.app.set_type(self.Type.STRING, self.Type.BYTES)
        yield self.Process(request, context, response)

    def Predict_String_ArrInt(self,
                              request: rekcurd_pb2.StringInput,
                              context: ServicerContext
                              ) -> rekcurd_pb2.ArrIntOutput:
        response = rekcurd_pb2.ArrIntOutput()
        self.rekcurd_pack.app.set_type(self.Type.STRING, self.Type.ARRAY_INT)
        return self.Process(request, context, response)

    def Predict_String_ArrFloat(self,
                                request: rekcurd_pb2.StringInput,
                                context: ServicerContext
                                ) -> rekcurd_pb2.ArrFloatOutput:
        response = rekcurd_pb2.ArrFloatOutput()
        self.rekcurd_pack.app.set_type(self.Type.STRING, self.Type.ARRAY_FLOAT)
        return self.Process(request, context, response)

    def Predict_String_ArrString(self,
                                 request: rekcurd_pb2.StringInput,
                                 context: ServicerContext
                                 ) -> rekcurd_pb2.ArrStringOutput:
        response = rekcurd_pb2.ArrStringOutput()
        self.rekcurd_pack.app.set_type(self.Type.STRING, self.Type.ARRAY_STRING)
        return self.Process(request, context, response)

    def Predict_Bytes_String(self,
                             request_iterator: Iterator[rekcurd_pb2.BytesInput],
                             context: ServicerContext
                             ) -> rekcurd_pb2.StringOutput:
        for request in request_iterator:
            response = rekcurd_pb2.StringOutput()
            self.rekcurd_pack.app.set_type(self.Type.BYTES, self.Type.STRING)
            return self.Process(request, context, response)

    def Predict_Bytes_Bytes(self,
                            request_iterator: Iterator[rekcurd_pb2.BytesInput],
                            context: ServicerContext
                            ) -> rekcurd_pb2.BytesOutput:
        for request in request_iterator:
            response = rekcurd_pb2.BytesOutput()
            self.rekcurd_pack.app.set_type(self.Type.BYTES, self.Type.BYTES)
            yield self.Process(request, context, response)

    def Predict_Bytes_ArrInt(self,
                             request_iterator: Iterator[rekcurd_pb2.BytesInput],
                             context: ServicerContext
                             ) -> rekcurd_pb2.ArrIntOutput:
        for request in request_iterator:
            response = rekcurd_pb2.ArrIntOutput()
            self.rekcurd_pack.app.set_type(self.Type.BYTES, self.Type.ARRAY_INT)
            return self.Process(request, context, response)

    def Predict_Bytes_ArrFloat(self,
                               request_iterator: Iterator[rekcurd_pb2.BytesInput],
                               context: ServicerContext
                               ) -> rekcurd_pb2.ArrFloatOutput:
        for request in request_iterator:
            response = rekcurd_pb2.ArrFloatOutput()
            self.rekcurd_pack.app.set_type(self.Type.BYTES, self.Type.ARRAY_FLOAT)
            return self.Process(request, context, response)

    def Predict_Bytes_ArrString(self,
                                request_iterator: Iterator[rekcurd_pb2.BytesInput],
                                context: ServicerContext
                                ) -> rekcurd_pb2.ArrStringOutput:
        for request in request_iterator:
            response = rekcurd_pb2.ArrStringOutput()
            self.rekcurd_pack.app.set_type(self.Type.BYTES, self.Type.ARRAY_STRING)
            return self.Process(request, context, response)

    def Predict_ArrInt_String(self,
                              request: rekcurd_pb2.ArrIntInput,
                              context: ServicerContext
                              ) -> rekcurd_pb2.StringOutput:
        response = rekcurd_pb2.StringOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_INT, self.Type.STRING)
        return self.Process(request, context, response)

    def Predict_ArrInt_Bytes(self,
                             request: rekcurd_pb2.ArrIntInput,
                             context: ServicerContext
                             ) -> rekcurd_pb2.BytesOutput:
        response = rekcurd_pb2.BytesOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_INT, self.Type.BYTES)
        yield self.Process(request, context, response)

    def Predict_ArrInt_ArrInt(self,
                              request: rekcurd_pb2.ArrIntInput,
                              context: ServicerContext
                              ) -> rekcurd_pb2.ArrIntOutput:
        response = rekcurd_pb2.ArrIntOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_INT, self.Type.ARRAY_INT)
        return self.Process(request, context, response)

    def Predict_ArrInt_ArrFloat(self,
                                request: rekcurd_pb2.ArrIntInput,
                                context: ServicerContext
                                ) -> rekcurd_pb2.ArrFloatOutput:
        response = rekcurd_pb2.ArrFloatOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_INT, self.Type.ARRAY_FLOAT)
        return self.Process(request, context, response)

    def Predict_ArrInt_ArrString(self,
                                 request: rekcurd_pb2.ArrIntInput,
                                 context: ServicerContext
                                 ) -> rekcurd_pb2.ArrStringOutput:
        response = rekcurd_pb2.ArrStringOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_INT, self.Type.ARRAY_STRING)
        return self.Process(request, context, response)

    def Predict_ArrFloat_String(self,
                                request: rekcurd_pb2.ArrFloatInput,
                                context: ServicerContext
                                ) -> rekcurd_pb2.StringOutput:
        response = rekcurd_pb2.StringOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_FLOAT, self.Type.STRING)
        return self.Process(request, context, response)

    def Predict_ArrFloat_Bytes(self,
                               request: rekcurd_pb2.ArrFloatInput,
                               context: ServicerContext
                               ) -> rekcurd_pb2.BytesOutput:
        response = rekcurd_pb2.BytesOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_FLOAT, self.Type.BYTES)
        yield self.Process(request, context, response)

    def Predict_ArrFloat_ArrInt(self,
                                request: rekcurd_pb2.ArrFloatInput,
                                context: ServicerContext
                                ) -> rekcurd_pb2.ArrIntOutput:
        response = rekcurd_pb2.ArrIntOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_FLOAT, self.Type.ARRAY_INT)
        return self.Process(request, context, response)

    def Predict_ArrFloat_ArrFloat(self,
                                  request: rekcurd_pb2.ArrFloatInput,
                                  context: ServicerContext
                                  ) -> rekcurd_pb2.ArrFloatOutput:
        response = rekcurd_pb2.ArrFloatOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_FLOAT, self.Type.ARRAY_FLOAT)
        return self.Process(request, context, response)

    def Predict_ArrFloat_ArrString(self,
                                   request: rekcurd_pb2.ArrFloatInput,
                                   context: ServicerContext
                                   ) -> rekcurd_pb2.ArrStringOutput:
        response = rekcurd_pb2.ArrStringOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_FLOAT, self.Type.ARRAY_STRING)
        return self.Process(request, context, response)

    def Predict_ArrString_String(self,
                                 request: rekcurd_pb2.ArrStringInput,
                                 context: ServicerContext
                                 ) -> rekcurd_pb2.StringOutput:
        response = rekcurd_pb2.StringOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_STRING, self.Type.STRING)
        return self.Process(request, context, response)

    def Predict_ArrString_Bytes(self,
                                request: rekcurd_pb2.ArrStringInput,
                                context: ServicerContext
                                ) -> rekcurd_pb2.BytesOutput:
        response = rekcurd_pb2.BytesOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_STRING, self.Type.BYTES)
        yield self.Process(request, context, response)

    def Predict_ArrString_ArrInt(self,
                                 request: rekcurd_pb2.ArrStringInput,
                                 context: ServicerContext
                                 ) -> rekcurd_pb2.ArrIntOutput:
        response = rekcurd_pb2.ArrIntOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_STRING, self.Type.ARRAY_INT)
        return self.Process(request, context, response)

    def Predict_ArrString_ArrFloat(self,
                                   request: rekcurd_pb2.ArrStringInput,
                                   context: ServicerContext
                                   ) -> rekcurd_pb2.ArrFloatOutput:
        response = rekcurd_pb2.ArrFloatOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_STRING, self.Type.ARRAY_FLOAT)
        return self.Process(request, context, response)

    def Predict_ArrString_ArrString(self,
                                    request: rekcurd_pb2.ArrStringInput,
                                    context: ServicerContext
                                    ) -> rekcurd_pb2.ArrStringOutput:
        response = rekcurd_pb2.ArrStringOutput()
        self.rekcurd_pack.app.set_type(self.Type.ARRAY_STRING, self.Type.ARRAY_STRING)
        return self.Process(request, context, response)
