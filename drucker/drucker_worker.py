#!/usr/bin/python
# -*- coding: utf-8 -*-


from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List, Tuple, Generator
from sqlalchemy.sql import exists

from .utils import DruckerConfig, PredictLabel, PredictResult, EvaluateResult, EvaluateDetail, EvaluateResultDetail
from .logger import logger
from .models import db, ModelAssignment


class Drucker(metaclass=ABCMeta):
    __type_input = None
    __type_output = None
    config = None
    logger = None
    db = None
    predictor = None
    model_path = None

    def __init__(self, config_file: str = None):
        self.config = DruckerConfig(config_file)
        self.logger = logger
        self.db = db
        self.logger.init_app(self.config)
        self.db.init_app(self.config)

        if self.config.TEST_MODE:
            self.db.ModelBase.metadata.drop_all(self.db.engine)
        self.db.ModelBase.metadata.create_all(self.db.engine)

        if not self.db.session.query(exists().where(ModelAssignment.service_name == self.config.SERVICE_NAME)).scalar():
            model_assignment = ModelAssignment()
            model_assignment.service_name = self.config.SERVICE_NAME
            model_assignment.model_path = self.config.FILE_MODEL
            model_assignment.first_boot = True
            self.db.session.add(model_assignment)
            self.db.session.commit()

        self.model_path = self.get_model_path()

    def is_first_boot(self) -> bool:
        try:
            model_assignment = self.db.session.query(ModelAssignment).filter(ModelAssignment.service_name == self.config.SERVICE_NAME).one()
            return model_assignment.first_boot
        except:
            return True

    def get_model_path(self, model_path: str = None) -> str:
        if model_path is None:
            model_path = self.config.FILE_MODEL
            result = self.db.session.query(ModelAssignment). \
                filter(ModelAssignment.service_name == self.config.SERVICE_NAME). \
                one_or_none()
            if result is not None:
                model_path = result.model_path
        return "{0}/{1}/{2}".format(self.config.DIR_MODEL, self.config.APPLICATION_NAME, model_path)

    def get_eval_path(self, eval_path: str) -> str:
        return "{0}/{1}/{2}".format(self.config.DIR_EVAL, self.config.APPLICATION_NAME, eval_path)

    def set_type(self, type_input: Enum, type_output: Enum) -> None:
        self.__type_input = type_input
        self.__type_output = type_output

    def get_type_input(self) -> Enum:
        return self.__type_input

    def get_type_output(self) -> Enum:
        return self.__type_output

    @abstractmethod
    def load_model(self) -> None:
        raise NotImplemented()

    @abstractmethod
    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        raise NotImplemented()

    @abstractmethod
    def evaluate(self, file_path: str) -> Tuple[EvaluateResult, List[EvaluateResultDetail]]:
        raise NotImplemented()

    @abstractmethod
    def get_evaluate_detail(self, file_path: str, results: List[EvaluateResultDetail]) -> Generator[EvaluateDetail, None, None]:
        raise NotImplemented()
