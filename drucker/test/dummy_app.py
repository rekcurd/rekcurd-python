#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Tuple, Generator

from drucker import Drucker
from drucker.utils import PredictLabel, PredictResult, EvaluateResult, EvaluateDetail, EvaluateResultDetail


class DummyApp(Drucker):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)

    def load_model(self) -> None:
        pass

    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        pass

    def evaluate(self, file_path: str) -> Tuple[EvaluateResult, List[EvaluateResultDetail]]:
        pass

    def get_evaluate_detail(self, file_path: str, results: List[EvaluateResultDetail]) -> Generator[EvaluateDetail, None, None]:
        pass
