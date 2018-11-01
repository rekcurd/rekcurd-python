#!/usr/bin/python
# -*- coding: utf-8 -*-


from drucker import Drucker
from drucker.utils import PredictLabel, PredictResult, EvaluateResult


class DummyApp(Drucker):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)

    def load_model(self) -> None:
        pass

    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        pass

    def evaluate(self, file: bytes) -> EvaluateResult:
        pass
