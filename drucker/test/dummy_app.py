#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Tuple, Iterator, Generator

from drucker import Drucker
from drucker.utils import PredictLabel, PredictResult, EvaluateResult, EvaluateDetail, EvaluateData


class DummyApp(Drucker):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)

    def load_model(self) -> None:
        pass

    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        pass

    def evaluate(self, eva_data: Iterator[EvaluateData]) -> Tuple[EvaluateResult, List[EvaluateDetail]]:
        pass

    def parse_eval_data(self, file_path: str) -> Generator[EvaluateData, None, None]:
        pass
