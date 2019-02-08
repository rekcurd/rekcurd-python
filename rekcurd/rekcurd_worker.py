#!/usr/bin/python
# -*- coding: utf-8 -*-


from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List, Tuple, Generator

from .utils import RekcurdConfig, PredictInput, PredictResult, EvaluateResult, EvaluateDetail, EvaluateResultDetail
from .logger import system_logger, service_logger, SystemLoggerInterface, ServiceLoggerInterface
from .data_servers import data_server, DataServer


class Rekcurd(metaclass=ABCMeta):
    """
    Rekcurd
    """
    config: RekcurdConfig = None
    system_logger: SystemLoggerInterface = None
    service_logger: ServiceLoggerInterface = None
    data_server: DataServer = None
    predictor: object = None

    def __init__(self, config_file: str = None):
        self.config = RekcurdConfig(config_file)
        self.system_logger = system_logger
        self.system_logger.init_app(self.config)
        self.service_logger = service_logger
        self.service_logger.init_app(self.config)
        self.data_server = data_server
        self.data_server.init_app(self.config)
        self.predictor = None

    def set_system_logger(self, logger: SystemLoggerInterface):
        self.system_logger = logger

    def set_service_logger(self, logger: ServiceLoggerInterface):
        self.service_logger = logger

    @abstractmethod
    def load_model(self, filepath: str) -> object:
        """
        load_model
        :param filepath:
        :return:
            predictor: Your predictor
        """
        raise NotImplemented()

    @abstractmethod
    def predict(self, predictor: object, input: PredictInput, option: dict = None) -> PredictResult:
        """
        predict
        :param predictor: Your predictor
        :param input:
        :param option:
        :return:
        """
        raise NotImplemented()

    @abstractmethod
    def evaluate(self, predictor: object, filepath: str) -> Tuple[EvaluateResult, List[EvaluateResultDetail]]:
        """
        evaluate
        :param predictor: Your predictor
        :param filepath:
        :return:
        """
        raise NotImplemented()

    @abstractmethod
    def get_evaluate_detail(self, filepath: str, results: List[EvaluateResultDetail]) -> Generator[EvaluateDetail, None, None]:
        """
        get_evaluate_detail
        :param filepath:
        :param results:
        :return:
        """
        raise NotImplemented()

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
