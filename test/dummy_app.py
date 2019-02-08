#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Tuple, Generator

from rekcurd import Rekcurd
from rekcurd.utils import PredictLabel, PredictResult, EvaluateResult, EvaluateDetail, EvaluateResultDetail


class DummyApp(Rekcurd):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)

    def load_model(self) -> None:
        pass

    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        pass

    def evaluate(self, filepath: str) -> Tuple[EvaluateResult, List[EvaluateResultDetail]]:
        pass

    def get_evaluate_detail(self, filepath: str, results: List[EvaluateResultDetail]) -> Generator[EvaluateDetail, None, None]:
        pass
