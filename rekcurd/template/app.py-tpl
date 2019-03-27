#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example is available on https://github.com/rekcurd/rekcurd-example/tree/master/python/sklearn-digits


from typing import Generator

from rekcurd import Rekcurd
from rekcurd.utils import PredictInput, PredictResult, EvaluateResult, EvaluateDetail, EvaluateResultDetail


class RekcurdAppTemplateApp(Rekcurd):
    def load_model(self, filepath: str) -> object:
        """ override
        TODO: Implement "load_model"
        :param filepath: ML model file path. str
        :return predictor: Your ML predictor object. object
        """
        pass

    def predict(self, predictor: object, idata: PredictInput, option: dict = None) -> PredictResult:
        """ override
        TODO: Implement "predict"
        :param predictor: Your ML predictor object. object
        :param idata: Input data. PredictInput, one of string/bytes/arr[int]/arr[float]/arr[string]
        :param option: Miscellaneous. dict
        :return result: Result. PredictResult
            result.label: Label. One of string/bytes/arr[int]/arr[float]/arr[string]
            result.score: Score. One of float/arr[float]
            result.option: Miscellaneous. dict
        """
        pass

    def evaluate(self, predictor: object, filepath: str) -> Generator[EvaluateResultDetail, None, EvaluateResult]:
        """ override
        TODO: Implement "evaluate"
        :param predictor: Your ML predictor object. object
        :param filepath: Evaluation data file path. str
        :return result: Result. EvaluateResult
            result.num: Number of data. int
            result.accuracy: Accuracy. float
            result.precision: Precision. arr[float]
            result.recall: Recall. arr[float]
            result.fvalue: F1 value. arr[float]
            result.option: Optional metrics. dict[str, float]
        :return detail[]: Detail result of each prediction. List[EvaluateResultDetail]
            detail[].result: Prediction result. PredictResult
            detail[].is_correct: Prediction result is correct or not. bool
        """
        pass

    def get_evaluate_detail(self, filepath: str, details: Generator[EvaluateResultDetail, None, None]) -> Generator[EvaluateDetail, None, None]:
        """ override
        TODO: Implement "get_evaluate_detail"
        :param filepath: Evaluation data file path. str
        :param details: Detail result of each prediction. List[EvaluateResultDetail]
        :return rtn: Return results. Generator[EvaluateDetail, None, None]
            rtn.input: Input data. PredictInput, one of string/bytes/arr[int]/arr[float]/arr[string]
            rtn.label: Predict label. PredictLabel, one of string/bytes/arr[int]/arr[float]/arr[string]
            rtn.result: Predict detail. EvaluateResultDetail
        """
        pass


if __name__ == '__main__':
    app = RekcurdAppTemplateApp()
    app.load_config_file("./settings.yml")
    app.run()
