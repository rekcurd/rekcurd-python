#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback

import grpc
import types
import shutil
import uuid
import pickle
import sys
from pathlib import Path

from grpc import ServicerContext
from typing import Iterator, Union, List

from .logger import SystemLoggerInterface
from .drucker_worker import Drucker, db, ModelAssignment
from .protobuf import drucker_pb2, drucker_pb2_grpc
from .utils import PredictInput, PredictLabel, PredictScore


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
                # DB rollback
                db.session.rollback()

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
            finally:
                db.session.close()

        return _wrapper

    return _wrapper_maker


class DruckerDashboardServicer(drucker_pb2_grpc.DruckerDashboardServicer):
    """ gRPC servicer to manage environment

    - Applications
        Machine leagning applications
    - Services
        Unit to deploy machine learning models
        (Corresponding to Service of K8S)
    - Models
        Machine learning model
    """

    # postfix for evaluate result
    EVALUATE_RESULT = '_eval_res.pkl'
    EVALUATE_DETAIL = '_eval_detail.pkl'

    CHUNK_SIZE = 100
    BYTE_LIMIT = 4190000

    def __init__(self, logger: SystemLoggerInterface, app: Drucker):
        self.logger = logger
        self.app = app

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

    def is_valid_upload_filename(self, filename: str) -> bool:
        if Path(filename).name == filename:
            return True
        return False

    def ServiceInfo(self,
                    request: drucker_pb2.ServiceInfoRequest,
                    context: ServicerContext
                    ) -> drucker_pb2.ServiceInfoResponse:
        """ Get service info.
        """
        return drucker_pb2.ServiceInfoResponse(
            application_name=self.app.config.APPLICATION_NAME,
            service_name=self.app.config.SERVICE_NAME,
            service_level=self.app.config.SERVICE_LEVEL_ENUM.value)

    @error_handling(drucker_pb2.ModelResponse(status=0, message='Error: Uploading model file.'))
    def UploadModel(self,
                    request_iterator: Iterator[drucker_pb2.UploadModelRequest],
                    context: ServicerContext
                    ) -> drucker_pb2.ModelResponse:
        """ Upload your latest ML model.
        """
        first_req = next(request_iterator)
        save_path = first_req.path
        if not self.is_valid_upload_filename(save_path):
            raise Exception(f'Error: Invalid model path specified -> {save_path}')

        tmp_path = self.app.get_model_path(uuid.uuid4().hex)
        Path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_path, 'wb') as f:
            f.write(first_req.data)
            for request in request_iterator:
                f.write(request.data)
            del first_req
            f.close()

        model_path = self.app.get_model_path(save_path)
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(tmp_path, model_path)
        return drucker_pb2.ModelResponse(status=1,
                                         message='Success: Uploading model file.')

    @error_handling(drucker_pb2.ModelResponse(status=0, message='Error: Switching model file.'))
    def SwitchModel(self,
                    request: drucker_pb2.SwitchModelRequest,
                    context: ServicerContext
                    ) -> drucker_pb2.ModelResponse:
        """ Switch your ML model to run.
        """
        if not self.is_valid_upload_filename(request.path):
            raise Exception(f'Error: Invalid model path specified -> {request.path}')

        model_assignment = self.app.db.session.query(ModelAssignment).filter(ModelAssignment.service_name == self.app.config.SERVICE_NAME).one()
        model_assignment.model_path = request.path
        model_assignment.first_boot = False
        self.app.db.session.commit()

        # :TODO: Use enum for SERVICE_INFRA
        if self.app.config.SERVICE_INFRA == "kubernetes":
            pass
        elif self.app.config.SERVICE_INFRA == "default":
            self.app.model_path = self.app.get_model_path()
            self.app.load_model()

        return drucker_pb2.ModelResponse(status=1,
                                         message='Success: Switching model file.')

    @error_handling(drucker_pb2.EvaluateModelResponse())
    def EvaluateModel(self,
                      request_iterator: Iterator[drucker_pb2.EvaluateModelRequest],
                      context: ServicerContext
                      ) -> drucker_pb2.EvaluateModelResponse:
        """ Evaluate your ML model and save result.
        """
        first_req = next(request_iterator)
        data_path = first_req.data_path
        result_path = first_req.result_path
        if not self.is_valid_upload_filename(data_path):
            raise Exception(f'Error: Invalid evaluation file path specified -> {data_path}')
        if not self.is_valid_upload_filename(result_path):
            raise Exception(f'Error: Invalid evaluation result file path specified -> {result_path}')

        result, details = self.app.evaluate(self.app.get_eval_path(data_path))
        metrics = drucker_pb2.EvaluationMetrics(num=result.num,
                                                accuracy=result.accuracy,
                                                precision=result.precision,
                                                recall=result.recall,
                                                fvalue=result.fvalue,
                                                option=result.option)

        eval_result_path = self.app.get_eval_path(result_path)
        Path(eval_result_path).parent.mkdir(parents=True, exist_ok=True)
        with open(eval_result_path + self.EVALUATE_RESULT, 'wb') as f:
            pickle.dump(result, f)
        with open(eval_result_path + self.EVALUATE_DETAIL, 'wb') as f:
            pickle.dump(details, f)

        return drucker_pb2.EvaluateModelResponse(metrics=metrics)

    @error_handling(drucker_pb2.UploadEvaluationDataResponse(status=0, message='Error: Uploading evaluation data.'))
    def UploadEvaluationData(self,
                             request_iterator: Iterator[drucker_pb2.UploadEvaluationDataRequest],
                             context: ServicerContext
                             ) -> drucker_pb2.UploadEvaluationDataResponse:
        """ Save evaluation data
        """
        first_req = next(request_iterator)
        save_path = first_req.data_path
        if not self.is_valid_upload_filename(save_path):
            raise Exception(f'Error: Invalid evaluation file path specified -> {save_path}')

        eval_data = b''.join([first_req.data] + [r.data for r in request_iterator])
        eval_path = self.app.get_eval_path(save_path)
        Path(eval_path).parent.mkdir(parents=True, exist_ok=True)
        with open(eval_path, 'wb') as f:
            f.write(eval_data)

        return drucker_pb2.UploadEvaluationDataResponse(status=1,
                                                        message='Success: Uploading evaluation data.')

    @error_handling(drucker_pb2.EvaluationResultResponse())
    def EvaluationResult(self,
                         request: drucker_pb2.EvaluationResultRequest,
                         context: ServicerContext
                         ) -> Iterator[drucker_pb2.EvaluationResultResponse]:
        """ Return saved evaluation result
        """
        data_path = request.data_path
        result_path = request.result_path
        if not self.is_valid_upload_filename(data_path):
            raise Exception(f'Error: Invalid evaluation file path specified -> {data_path}')
        if not self.is_valid_upload_filename(result_path):
            raise Exception(f'Error: Invalid evaluation result file path specified -> {result_path}')

        eval_result_path = self.app.get_eval_path(result_path)
        with open(eval_result_path + self.EVALUATE_DETAIL, 'rb') as f:
            result_details = pickle.load(f)
        with open(eval_result_path + self.EVALUATE_RESULT, 'rb') as f:
            result = pickle.load(f)
        metrics = drucker_pb2.EvaluationMetrics(num=result.num,
                                                accuracy=result.accuracy,
                                                precision=result.precision,
                                                recall=result.recall,
                                                fvalue=result.fvalue,
                                                option=result.option)

        detail_chunks = []
        detail_chunk = []
        metrics_size = sys.getsizeof(metrics)
        for detail in self.app.get_evaluate_detail(self.app.get_eval_path(data_path), result_details):
            detail_chunk.append(drucker_pb2.EvaluationResultResponse.Detail(
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
                    yield drucker_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunks)
                    detail_chunks = detail_chunk
                detail_chunk = []

        if len(detail_chunks + detail_chunk) > 0:
            if metrics_size + sys.getsizeof(detail_chunk + detail_chunks) < self.BYTE_LIMIT:
                detail_chunks.extend(detail_chunk)
                yield drucker_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunks)
            else:
                yield drucker_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunks)
                yield drucker_pb2.EvaluationResultResponse(metrics=metrics, detail=detail_chunk)

    def get_io_by_type(self, io: Union[PredictInput, PredictLabel]) -> drucker_pb2.IO:
        if not isinstance(io, list):
            io = [io]

        if len(io) == 0:
            return drucker_pb2.IO(tensor=drucker_pb2.Tensor())
        if isinstance(io[0], str):
            return drucker_pb2.IO(str=drucker_pb2.ArrString(val=io))
        else:
            return drucker_pb2.IO(tensor=drucker_pb2.Tensor(shape=[1], val=io))

    def get_score_by_type(self, score: PredictScore) -> List[float]:
        if isinstance(score, list):
            return score
        else:
            return [score]
