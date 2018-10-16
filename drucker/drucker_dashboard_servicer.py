#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback

import grpc
import types
import shutil
import uuid
from pathlib import Path

from grpc._server import _Context
from typing import Iterator

from .logger import SystemLoggerInterface
from .drucker_worker import Drucker, db, ModelAssignment
from .protobuf import drucker_pb2, drucker_pb2_grpc


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

    def ServiceInfo(self,
                    request: drucker_pb2.ServiceInfoRequest,
                    context: _Context
                    ) -> drucker_pb2.ServiceInfoResponse:
        """ Get service info.
        """
        return drucker_pb2.ServiceInfoResponse(
            application_name=self.app.config.APPLICATION_NAME,
            service_name=self.app.config.SERVICE_NAME,
            service_level=self.app.config.SERVICE_LEVEL)

    @error_handling(drucker_pb2.ModelResponse(status=0, message='Error: Uploading model file.'))
    def UploadModel(self,
                    request_iterator: Iterator[drucker_pb2.UploadModelRequest],
                    context: _Context
                    ) -> drucker_pb2.ModelResponse:
        """ Upload your latest ML model.
        """
        save_path = None
        tmp_path = self.app.get_model_path(uuid.uuid4().hex)
        Path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_path, 'wb') as f:
            for request in request_iterator:
                save_path = request.path
                model_data = request.data
                f.write(model_data)
            f.close()
        model_path = self.app.get_model_path(save_path)
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(tmp_path, model_path)
        return drucker_pb2.ModelResponse(status=1,
                                         message='Success: Uploading model file.')

    @error_handling(drucker_pb2.ModelResponse(status=0, message='Error: Switching model file.'))
    def SwitchModel(self,
                    request: drucker_pb2.SwitchModelRequest,
                    context: _Context
                    ) -> drucker_pb2.ModelResponse:
        """ Switch your ML model to run.
        """
        model_assignment = self.app.db.session.query(ModelAssignment).filter(ModelAssignment.service_name == self.app.config.SERVICE_NAME).one()
        model_assignment.model_path = request.path
        model_assignment.first_boot = False
        self.app.db.session.commit()
        model_path = self.app.get_model_path()

        # :TODO: Use enum for SERVICE_INFRA
        if self.app.config.SERVICE_INFRA == "kubernetes":
            pass
        elif self.app.config.SERVICE_INFRA == "default":
            self.app.load_model(model_path)

        return drucker_pb2.ModelResponse(status=1,
                                         message='Success: Switching model file.')

    def EvaluateModel(self,
                      request_iterator: Iterator[drucker_pb2.EvaluateModelRequest],
                      context: _Context
                      ) -> drucker_pb2.EvaluateModelResponse:
        """ Evaluate your ML model.
        :TODO: in detail.
        """
        try:
            for evaluateModelRequest in request_iterator:
                test_data = evaluateModelRequest.data
                result = self.app.evaluate(test_data)
                return drucker_pb2.EvaluateModelResponse(num=result.num,
                                                         accuracy=result.accuracy,
                                                         precision=result.precision,
                                                         recall=result.recall,
                                                         fvalue=result.fvalue)
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            return drucker_pb2.EvaluateModelResponse(num=0,
                                                     accuracy=0,
                                                     precision=0,
                                                     recall=0,
                                                     fvalue=0)
