#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Union, List

PredictLabel = Union[str, bytes, List[str], List[int], List[float]]
PredictScore = Union[float, List[float]]


class PredictResult:
    def __init__(self, label: PredictLabel, score: PredictScore, option: dict = {}):
        self.label = label
        self.score = score
        self.option = json.dumps(option)


class EvaluateResult:
    def __init__(self, num: int = None, accuracy: float = None,
                 precision: list = None, recall: list = None,
                 fvalue: list = None):
        if num is None:
            self.num = 0
            self.accuracy = 0.0
            self.precision = [0]
            self.recall = [0]
            self.fvalue = [0]
        else:
            self.num = num
            self.accuracy = accuracy
            self.precision = precision
            self.recall = recall
            self.fvalue = fvalue


class PredictInterface(metaclass=ABCMeta):
    def __init__(self):
        self.type_input = None
        self.type_output = None

    def set_type(self, type_input: Enum, type_output: Enum) -> None:
        self.type_input = type_input
        self.type_output = type_output

    def get_type_input(self) -> Enum:
        return self.type_input

    def get_type_output(self) -> Enum:
        return self.type_output

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        raise NotImplemented()

    @abstractmethod
    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        raise NotImplemented()

    @abstractmethod
    def evaluate(self, file: bytes) -> EvaluateResult:
        raise NotImplemented()
