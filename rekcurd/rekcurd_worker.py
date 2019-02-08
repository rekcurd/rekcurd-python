#!/usr/bin/python
# -*- coding: utf-8 -*-


from abc import ABCMeta
from enum import Enum

from .utils import RekcurdConfig
from .logger import SystemLoggerInterface, ServiceLoggerInterface, JsonSystemLogger, JsonServiceLogger
from .data_servers import DataServer


class Rekcurd(metaclass=ABCMeta):
    """
    Rekcurd
    """
    _system_logger: SystemLoggerInterface = None
    _service_logger: ServiceLoggerInterface = None

    config: RekcurdConfig = None
    data_server: DataServer = None
    predictor: object = None

    def __init__(self, config_file: str = None):
        self.config = RekcurdConfig(config_file)
        self._system_logger = JsonSystemLogger(self.config)
        self._service_logger = JsonServiceLogger(self.config)
        self.data_server = DataServer(self.config)
        self.predictor = None
        self.rekcurd_functions = dict()

    @property
    def system_logger(self):
        return self._system_logger

    @system_logger.setter
    def system_logger(self, system_logger: SystemLoggerInterface):
        self._system_logger = system_logger

    @property
    def service_logger(self):
        return self._service_logger

    @service_logger.setter
    def service_logger(self, service_logger: ServiceLoggerInterface):
        self._service_logger = service_logger

    def load_model(self, func):
        """
        load_model decorator.
        :param func: Your method.

        Following IO specs is required for your method.
        :param filepath: ML model file path. str
        :return predictor: Your ML predictor object. object
        """
        def wrapper(*args, **kwargs):
            if len(args) != 1:
                raise TypeError("{}() needs to take 1 argument.\n"
                                "  :param filepath: ML model file path. str\n"
                                "  :return predictor: Your ML predictor object. object\n".format(func.__name__))
            func(*args, **kwargs)
        self.rekcurd_functions["load_model"] = func
        return wrapper

    def predict(self, func):
        """
        predict decorator.
        :param func: Your method.

        Following IO specs is required for your method.
        :param predictor: Your ML predictor object. object
        :param input: Input data. PredictInput, one of string/bytes/arr[int]/arr[float]/arr[string]
        :param option=None: Miscellaneous. dict
        :return rtn: Result. PredictResult
            rtn.output: Output. One of string/bytes/arr[int]/arr[float]/arr[string]
            rtn.score: Score. One of float/arr[float]
            rtn.option: Miscellaneous. dict
        """
        def wrapper(*args, **kwargs):
            if len(args) < 2 or len(args) > 3:
                raise TypeError("{}() needs to take 2 or 3 arguments.\n"
                                "  :param predictor: Your ML predictor object. object\n"
                                "  :param input: Input data. PredictInput, one of string/bytes/arr[int]/arr[float]/arr[string]\n"
                                "  :param option=None: Miscellaneous. dict\n"
                                "  :return rtn: Result. PredictResult\n"
                                "      rtn.output: Output. One of string/bytes/arr[int]/arr[float]/arr[string]\n"
                                "      rtn.score: Score. One of float/arr[float]\n"
                                "      rtn.option: Miscellaneous. dict\n".format(func.__name__))
            func(*args, **kwargs)
        self.rekcurd_functions["predict"] = func
        return wrapper

    def evaluate(self, func):
        """
        evaluate decorator.
        :param func: Your method.

        Following IO specs is required for your method.
        :param predictor: Your ML predictor object. object
        :param filepath: Evaluation data file path. str
        :return rst: Result. EvaluateResult
            rst.num: Number of data. int
            rst.accuracy: Accuracy. float
            rst.precision: Precision. arr[float]
            rst.recall: Recall. arr[float]
            rst.fvalue: F1 value. arr[float]
            rst.option: Optional metrics. dict[str, float]
        :return dtl: Detail result of each prediction. List[EvaluateResultDetail]
            dtl[].result: Prediction result. PredictResult
            dtl[].is_correct: Prediction result is correct or not. bool
        """
        def wrapper(*args, **kwargs):
            if len(args) != 2:
                raise TypeError("{}() needs to take 2 arguments.\n"
                                "  :param predictor: Your ML predictor object. object\n"
                                "  :param filepath: Evaluation data file path. str\n"
                                "  :return rst: Result. EvaluateResult\n"
                                "      rst.num: Number of data. int\n"
                                "      rst.accuracy: Accuracy. float\n"
                                "      rst.precision: Precision. arr[float]\n"
                                "      rst.recall: Recall. arr[float]\n"
                                "      rst.fvalue: F1 value. arr[float]\n"
                                "      rst.option: Optional metrics. dict[str, float]\n"
                                "  :return dtl: Detail result of each prediction. List[EvaluateResultDetail]\n"
                                "      dtl[].result: Prediction result. PredictResult\n"
                                "      dtl[].is_correct: Prediction result is correct or not. bool\n".format(func.__name__))
            func(*args, **kwargs)
        self.rekcurd_functions["evaluate"] = func
        return wrapper

    def get_evaluate_detail(self, func):
        """
        evaluate decorator.
        :param func: Your method.

        Following IO specs is required for your method.
        :param filepath: Evaluation data file path. str
        :param dtl: Detail result of each prediction. List[EvaluateResultDetail]
        :return rtn: Return results. Generator[EvaluateDetail, None, None]
            rtn.input: Input data. PredictInput, one of string/bytes/arr[int]/arr[float]/arr[string]
            rtn.label: Predict label. PredictLabel, one of string/bytes/arr[int]/arr[float]/arr[string]
            rtn.result: Predict detail. EvaluateResultDetail
        """
        def wrapper(*args, **kwargs):
            if len(args) != 2:
                raise TypeError("{}() needs to take 2 arguments.\n"
                                "  :param filepath: Evaluation data file path. str\n"
                                "  :param dtl: Detail result of each prediction. List[EvaluateResultDetail]\n"
                                "  :return rtn: Return results. Generator[EvaluateDetail, None, None]\n"
                                "      rtn.input: Input data. PredictInput, one of string/bytes/arr[int]/arr[float]/arr[string]\n"
                                "      rtn.label: Predict label. PredictLabel, one of string/bytes/arr[int]/arr[float]/arr[string]\n"
                                "      rtn.result: Predict detail. EvaluateResultDetail\n".format(func.__name__))
            func(*args, **kwargs)
        self.rekcurd_functions["get_evaluate_detail"] = func
        return wrapper

    def run(self, host: str = None, port: int = None, max_workers: int = None):
        import grpc
        import time
        from concurrent import futures
        from rekcurd.protobuf import rekcurd_pb2_grpc
        from rekcurd import RekcurdDashboardServicer, RekcurdWorkerServicer

        _host = "127.0.0.1"
        _port = 5000
        _max_workers = 1
        host = host or _host
        port = int(port or self.config.SERVICE_PORT or _port)
        max_workers = int(max_workers or _max_workers)

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        rekcurd_pb2_grpc.add_RekcurdDashboardServicer_to_server(
            RekcurdDashboardServicer(app=self), server)
        rekcurd_pb2_grpc.add_RekcurdWorkerServicer_to_server(
            RekcurdWorkerServicer(app=self), server)
        server.add_insecure_port("{0}:{1}".format(host, port))
        server.start()
        try:
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            self.system_logger.info("Shutdown rekcurd worker.")
            server.stop(0)

    # TODO: DEPRECATED BELOW
    __type_input = None
    __type_output = None

    def set_type(self, type_input: Enum, type_output: Enum) -> None:
        self.__type_input = type_input
        self.__type_output = type_output

    def get_type_input(self) -> Enum:
        return self.__type_input

    def get_type_output(self) -> Enum:
        return self.__type_output
