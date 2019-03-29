#!/usr/bin/python
# -*- coding: utf-8 -*-


import traceback

import grpc
import types
import pickle
import sys

from grpc import ServicerContext
from typing import Iterator, Union, List

from .rekcurd_worker import RekcurdPack
from rekcurd.protobuf import rekcurd_pb2, rekcurd_pb2_grpc
from rekcurd.utils import PredictInput, PredictLabel, PredictScore


def error_handling(error_response):
    """ Decorator for handling error

    Apply following processing on Servicer methods
    to handle errors.

    - DB transaction decorating for Servicer class.
      Confirm to call :func:``db.session.commit``
      on success operation and :func:``db.session.rollback``
      on fail.
    - Error setup for gRPC errors
    - Call :func:``on_error`` method (if defined) in the class
      to postprocess something on error

    Parameters
    ----------
    error_response
        gRPC response instance on error

    """

    def _wrapper_maker(func):
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                # gRPC
                context = args[2]
                context.set_code(grpc.StatusCode.UNKNOWN)
                context.set_details(str(error))

                servicer = args[0]
                if hasattr(servicer, 'on_error'):
                    assert isinstance(servicer.on_error, types.MethodType), \
                        'You must define on_error as method'
                    servicer.on_error(error)
                return error_response

        return _wrapper

    return _wrapper_maker


class RekcurdDashboardServicer(rekcurd_pb2_grpc.RekcurdDashboardServicer):
    """ gRPC servicer to manage environment

    - Applications
        Machine leagning applications
    - Services
        Unit to deploy machine learning models
        (Corresponding to Service of K8S)
    - Models
        Machine learning model
    """

    CHUNK_SIZE = 100
    BYTE_LIMIT = 4190000

    def __init__(self, rekcurd_pack: RekcurdPack):
        self.rekcurd_pack = rekcurd_pack
        self.logger = rekcurd_pack.app.system_logger

    def on_error(self, error: Exception):
        """ Postprocessing on error

        For detail, see :func:``on_error``

        Parameters
        ----------
        error : Exception
            Error to be handled
        """
        self.logger.error(str(error))
        self.logger.error(traceback.format_exc())

    def ServiceInfo(self,
                    request: rekcurd_pb2.ServiceInfoRequest,
                    context: ServicerContext
                    ) -> rekcurd_pb2.ServiceInfoResponse:
        """ Get service info.

        :param request:
        :param context:
        :return:
        """
        self.logger.info("Run ServiceInfo.")
        return rekcurd_pb2.ServiceInfoResponse(
            application_name=self.rekcurd_pack.app.config.APPLICATION_NAME,
            service_name=self.rekcurd_pack.app.config.SERVICE_ID,
            service_level=self.rekcurd_pack.app.config.SERVICE_LEVEL)

    @error_handling(rekcurd_pb2.ModelResponse(status=0, message='Error: Uploading model file.'))
    def UploadModel(self,
                    request_iterator: Iterator[rekcurd_pb2.UploadModelRequest],
                    context: ServicerContext
                    ) -> rekcurd_pb2.ModelResponse:
        """ Upload your latest ML model.

        :param request_iterator:
        :param context:
        :return:
        """
        self.logger.info("Run UploadModel.")
        self.rekcurd_pack.app.data_server.upload_model(request_iterator)
        return rekcurd_pb2.ModelResponse(status=1,
                                         message='Success: Uploading model file.')

    @error_handling(rekcurd_pb2.ModelResponse(status=0, message='Error: Switching model file.'))
    def SwitchModel(self,
                    request: rekcurd_pb2.SwitchModelRequest,
                    context: ServicerContext
                    ) -> rekcurd_pb2.ModelResponse:
        """ Switch your ML model.

        :param request:
        :param context:
        :return:
        """
        self.logger.info("Run SwitchModel.")
        filepath = request.path
        local_filepath = self.rekcurd_pack.app.data_server.switch_model(filepath)
        self.rekcurd_pack.predictor = self.rekcurd_pack.app.load_model(local_filepath)
        return rekcurd_pb2.ModelResponse(status=1,
                                         message='Success: Switching model file.')

    @error_handling(rekcurd_pb2.EvaluateModelResponse())
    def EvaluateModel(self,
                      request_iterator: Iterator[rekcurd_pb2.EvaluateModelRequest],
                      context: ServicerContext
                      ) -> rekcurd_pb2.EvaluateModelResponse:
        """ Evaluate your ML model and save result.

        :param request_iterator:
        :param context:
        :return:
        """
        self.logger.info("Run EvaluateModel.")
        first_req = next(request_iterator)
        data_path = first_req.data_path
        result_path = first_req.result_path

        local_data_path = self.rekcurd_pack.app.data_server.get_evaluation_data_path(data_path)
        evaluate_result_gen = self.rekcurd_pack.app.evaluate(self.rekcurd_pack.predictor, local_data_path)
        result = self.rekcurd_pack.app.data_server.upload_evaluation_result(evaluate_result_gen, result_path)
        label_ios = [self.get_io_by_type(l) for l in result.label]
        metrics = rekcurd_pb2.EvaluationMetrics(num=result.num,
                                                accuracy=result.accuracy,
                                                precision=result.precision,
                                                recall=result.recall,
                                                fvalue=result.fvalue,
                                                option=result.option,
                                                label=label_ios)
        return rekcurd_pb2.EvaluateModelResponse(metrics=metrics)

    @error_handling(rekcurd_pb2.UploadEvaluationDataResponse(status=0, message='Error: Uploading evaluation data.'))
    def UploadEvaluationData(self,
                             request_iterator: Iterator[rekcurd_pb2.UploadEvaluationDataRequest],
                             context: ServicerContext
                             ) -> rekcurd_pb2.UploadEvaluationDataResponse:
        """ Save evaluation data

        :param request_iterator:
        :param context:
        :return:
        """
        self.logger.info("Run UploadEvaluationData.")
        self.rekcurd_pack.app.data_server.upload_evaluation_data(request_iterator)
        return rekcurd_pb2.UploadEvaluationDataResponse(status=1,
                                                        message='Success: Uploading evaluation data.')

    @error_handling(rekcurd_pb2.EvaluationResultResponse())
    def EvaluationResult(self,
                         request: rekcurd_pb2.EvaluationResultRequest,
                         context: ServicerContext
                         ) -> Iterator[rekcurd_pb2.EvaluationResultResponse]:
        """ Return saved evaluation result
        """
        self.logger.info("Run EvaluationResult.")
        data_path = request.data_path
        result_path = request.result_path
        local_data_path = self.rekcurd_pack.app.data_server.get_evaluation_data_path(data_path)
        local_result_detail_path = self.rekcurd_pack.app.data_server.get_eval_result_detail(result_path)

        # TODO: deprecated. remove metrics from response in the next gRPC spec
        metrics = rekcurd_pb2.EvaluationMetrics()

        detail_chunks = []
        detail_chunk = []
        metrics_size = sys.getsizeof(metrics)
        with open(local_result_detail_path, 'rb') as detail_file:
            def generate_result_detail():
                try:
                    while True:
                        yield pickle.load(detail_file)
                except EOFError:
                    pass
            for detail in self.rekcurd_pack.app.get_evaluate_detail(local_data_path, generate_result_detail()):
                detail_chunk.append(rekcurd_pb2.EvaluationResultResponse.Detail(
                    input=self.get_io_by_type(detail.input),
                    label=self.get_io_by_type(detail.label),
                    output=self.get_io_by_type(detail.result.result.label),
                    score=self.get_score_by_type(detail.result.result.score),
                    is_correct=detail.result.is_correct
                ))
                if len(detail_chunk) == self.CHUNK_SIZE:
                    if metrics_size + sys.getsizeof(detail_chunk + detail_chunks) < self.BYTE_LIMIT:
                        detail_chunks.extend(detail_chunk)
                    else:
                        yield rekcurd_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunks)
                        detail_chunks = detail_chunk
                    detail_chunk = []

        if len(detail_chunks + detail_chunk) > 0:
            if metrics_size + sys.getsizeof(detail_chunk + detail_chunks) < self.BYTE_LIMIT:
                detail_chunks.extend(detail_chunk)
                yield rekcurd_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunks)
            else:
                yield rekcurd_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunks)
                yield rekcurd_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunk)

    def get_io_by_type(self, io: Union[PredictInput, PredictLabel]) -> rekcurd_pb2.IO:
        if not isinstance(io, list):
            io = [io]

        if len(io) == 0:
            return rekcurd_pb2.IO(tensor=rekcurd_pb2.Tensor())
        if isinstance(io[0], str):
            return rekcurd_pb2.IO(str=rekcurd_pb2.ArrString(val=io))
        else:
            return rekcurd_pb2.IO(tensor=rekcurd_pb2.Tensor(shape=[1], val=io))

    def get_score_by_type(self, score: PredictScore) -> List[float]:
        if isinstance(score, list):
            return score
        else:
            return [score]
