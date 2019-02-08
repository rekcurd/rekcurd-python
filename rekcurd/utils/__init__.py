# coding: utf-8


import json
from typing import Union, List, Dict, NamedTuple

from .rekcurd_config import RekcurdConfig, ModelModeEnum


PredictInput = Union[str, bytes, List[str], List[int], List[float]]
PredictLabel = Union[str, bytes, List[str], List[int], List[float]]
PredictScore = Union[float, List[float]]


class PredictResult:
    def __init__(self, label: PredictLabel, score: PredictScore, option: dict = None):
        self.label = label
        self.score = score
        self.option = json.dumps(option) if option is not None else '{}'


class EvaluateResult:
    def __init__(self, num: int, accuracy: float, precision: List[float],
                 recall: List[float], fvalue: List[float], label: List[PredictLabel],
                 option: Dict[str, float] = {}):
        self.num = num
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.fvalue = fvalue
        self.label = label
        self.option = option


class EvaluateResultDetail(NamedTuple):
    result: PredictResult
    is_correct: bool


class EvaluateDetail(NamedTuple):
    input: PredictInput
    label: PredictLabel
    result: EvaluateResultDetail


incoming_headers = [
    'x-request-id', 'x-b3-traceid', 'x-b3-spanid', 'x-b3-parentspanid',
    'x-b3-sampled', 'x-b3-flags', 'x-ot-span-context']

def getForwardHeaders(incoming: list) -> list:
    headers = list()
    for k,v in incoming:
        if k in incoming_headers:
            headers.append((k, v))
    return headers
