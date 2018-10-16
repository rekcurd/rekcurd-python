#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import csv
import os
import io

from enum import Enum

from drucker.logger import JsonSystemLogger
from drucker import Drucker
from drucker.utils import PredictLabel, PredictResult, EvaluateResult

### Expansion start. You can add your necessity libraries.
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

import zipfile
from sklearn.externals import joblib


def joblib_load_from_zip(zip_name: str, file_name: str):
    with zipfile.ZipFile(zip_name, 'r') as zf:
        with zf.open(file_name, 'r') as zipmodel:
            return joblib.load(io.BufferedReader(io.BytesIO(zipmodel.read())))
### Expansion end.


class MyApp(Drucker):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)
        self.logger = JsonSystemLogger(self.config)
        self.load_model()

    def set_type(self, type_input: Enum, type_output: Enum) -> None:
        super().set_type(type_input, type_output)

    def get_type_input(self) -> Enum:
        return super().get_type_input()

    def get_type_output(self) -> Enum:
        return super().get_type_output()

    def load_model(self) -> None:
        """ override
        Load ML model.
        :return:
        """
        assert self.model_path is not None, \
            'Please specify your ML model path'
        try:
            # FIXME: This is an example. Implement HERE!
            self.predictor = joblib.load(self.model_path)
            # FIXME: This is Another example. You can use archived file if your algorithm requires some files.
            # file_name = 'default.model'
            # self.predictor = joblib_load_from_zip(self.model_path, file_name)

        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            self.predictor = None
            if not self.is_first_boot():
                # noinspection PyProtectedMember
                os._exit(-1)

    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        """ override
        Predict.

        :param input: Input data. string/bytes/arr[int]/arr[float]/arr[string]
        :param option: Miscellaneous. dict
        :return:
            output: Result. string/bytes/arr[int]/arr[float]/arr[string]
            score: Score. float/arr[float]
            option: Miscellaneous. dict
        """
        try:
            # FIXME: This is an example. Implement HERE!
            if option is None:
                option = {}
            label_predict = self.predictor.predict(
                np.array([input], dtype='float64')).tolist()
            return PredictResult(label_predict, [1] * len(label_predict), option={})
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            raise e

    def evaluate(self, file: bytes) -> EvaluateResult:
        """ override
        Evaluate.
        :TODO: in detail.

        :param file: Evaluation data file. bytes
        :return:
            num: Number of data. int
            accuracy: Accuracy. float
            precision: Precision. arr[float]
            recall: Recall. arr[float]
            fvalue: F1 value. arr[float]
        """
        try:
            # FIXME: This is an example. Implement HERE!
            f = io.StringIO(file.decode("utf-8"))
            reader = csv.reader(f, delimiter=",")
            num = 0
            label_gold = []
            label_predict = []
            for row in reader:
                num += 1
                label_gold.append(int(row[0]))
                result = self.predict(row[1:], option={})
                label_predict.append(result.label)

            accuracy = accuracy_score(label_gold, label_predict)
            p_r_f = precision_recall_fscore_support(label_gold, label_predict)
            return EvaluateResult(num, accuracy, p_r_f[0].tolist(), p_r_f[1].tolist(), p_r_f[2].tolist())
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            return EvaluateResult()
