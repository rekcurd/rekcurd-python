#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Tuple, Generator

from rekcurd import Rekcurd
from rekcurd.utils import PredictInput, PredictResult, EvaluateResult, EvaluateDetail, EvaluateResultDetail


class DummyApp(Rekcurd):
    def load_model(self, filepath: str) -> object:
        pass

    def predict(self, predictor: object, idata: PredictInput, option: dict = None) -> PredictResult:
        pass

    def evaluate(self, predictor: object, filepath: str) -> Tuple[EvaluateResult, List[EvaluateResultDetail]]:
        pass

    def get_evaluate_detail(self, filepath: str, details: List[EvaluateResultDetail]) -> Generator[EvaluateDetail, None, None]:
        pass

app = DummyApp()
