# coding: utf-8


import os
import yaml
import json

from enum import Enum
from typing import Union, List, Dict, NamedTuple


PredictInput = Union[str, bytes, List[str], List[int], List[float]]
PredictLabel = Union[str, bytes, List[str], List[int], List[float]]
PredictScore = Union[float, List[float]]


class DruckerConfig:
    def __init__(self, config_file: str):
        settings_yaml = os.getenv("DRUCKER_SETTINGS_YAML", config_file)
        config = dict()
        if settings_yaml is not None:
            with open(settings_yaml, 'r') as f:
                config = yaml.load(f)
        self.TEST_MODE = str(os.getenv("DRUCKER_TEST_MODE", config.get("test", "False"))).lower() == 'true'
        self.SERVICE_PORT = os.getenv("DRUCKER_SERVICE_PORT", config.get("app.port", "5000"))
        self.APPLICATION_NAME = os.getenv("DRUCKER_APPLICATION_NAME", config["app.name"])
        self.SERVICE_NAME = os.getenv("DRUCKER_SERVICE_NAME", config["app.service.name"])
        service_level = os.getenv("DRUCKER_SERVICE_LEVEL", config["app.service.level"])
        self.SERVICE_LEVEL_ENUM = ServiceEnvType.to_Enum(service_level)
        self.SERVICE_INFRA = os.getenv("DRUCKER_SERVICE_INFRA", "default")
        self.DIR_MODEL = os.getenv("DRUCKER_SERVICE_MODEL_DIR", config.get("app.modeldir", "./model"))
        self.DIR_EVAL = os.getenv("DRUCKER_SERVICE_EVAL_DIR", config.get("app.evaldir", "./eval"))
        self.FILE_MODEL = os.getenv("DRUCKER_SERVICE_MODEL_FILE", config.get("app.modelfile", "default.model"))
        self.DB_MODE = os.getenv('DRUCKER_DB_MODE', config.get('use.db', "sqlite"))
        self.DB_MYSQL_HOST = os.getenv('DRUCKER_DB_MYSQL_HOST', config.get('db.mysql.host', ""))
        self.DB_MYSQL_PORT = os.getenv('DRUCKER_DB_MYSQL_PORT', config.get('db.mysql.port', ""))
        self.DB_MYSQL_DBNAME = os.getenv('DRUCKER_DB_MYSQL_DBNAME', config.get('db.mysql.dbname', ""))
        self.DB_MYSQL_USER = os.getenv('DRUCKER_DB_MYSQL_USER', config.get('db.mysql.user', ""))
        self.DB_MYSQL_PASSWORD = os.getenv('DRUCKER_DB_MYSQL_PASSWORD', config.get('db.mysql.password', ""))


class ServiceEnvType(Enum):
    DEVELOPMENT = 'development'
    BETA = 'beta'
    STAGING = 'staging'
    SANDBOX = 'sandbox'
    PRODUCTION = 'production'

    @classmethod
    def to_Enum(cls, istr: str):
        if cls.DEVELOPMENT.value == istr:
            return cls.DEVELOPMENT
        elif cls.BETA.value == istr:
            return cls.BETA
        elif cls.STAGING.value == istr:
            return cls.STAGING
        elif cls.SANDBOX.value == istr:
            return cls.SANDBOX
        elif cls.PRODUCTION.value == istr:
            return cls.PRODUCTION
        else:
            raise ValueError("'{}' is not supported as ServiceEnvType".format(istr))


class PredictResult:
    def __init__(self, label: PredictLabel, score: PredictScore, option: dict = None):
        self.label = label
        self.score = score
        self.option = json.dumps(option) if option is not None else '{}'


class EvaluateResult:
    def __init__(self, num: int = None, accuracy: float = None,
                 precision: List[float] = None, recall: List[float] = None,
                 fvalue: List[float] = None, option: Dict[str, float] = {}):
        if num is None:
            self.num = 0
            self.accuracy = 0.0
            self.precision = [0.0]
            self.recall = [0.0]
            self.fvalue = [0.0]
            self.option = {}
        else:
            self.num = num
            self.accuracy = accuracy
            self.precision = precision
            self.recall = recall
            self.fvalue = fvalue
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
