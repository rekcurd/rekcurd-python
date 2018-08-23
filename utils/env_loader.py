#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
import yaml
import os


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
        elif cls.PRODUCTION == istr:
            return cls.PRODUCTION
        else:
            return None


TEST_MODE = False if os.getenv("DRUCKER_TEST_MODE", None) is None else True

SETTINGS_YAML = os.getenv("DRUCKER_SETTINGS_YAML", "settings.yml")
config = yaml.load(open(SETTINGS_YAML, 'r'))

SERVICE_PORT = os.getenv("DRUCKER_SERVICE_PORT", config.get("app.port", "5000"))

APPLICATION_NAME = os.getenv("DRUCKER_APPLICATION_NAME", config["app.name"])
SERVICE_NAME = os.getenv("DRUCKER_SERVICE_NAME", config["app.service.name"])
SERVICE_LEVEL = os.getenv("DRUCKER_SERVICE_LEVEL", config["app.service.level"])
SERVICE_LEVEL_ENUM = ServiceEnvType.to_Enum(SERVICE_LEVEL)
SERVICE_INFRA = os.getenv("DRUCKER_SERVICE_INFRA", "default")

DIR_MODEL = os.getenv("DRUCKER_SERVICE_MODEL_DIR", config.get("app.modeldir", "./model"))
FILE_MODEL = os.getenv("DRUCKER_SERVICE_MODEL_FILE", config.get("app.modelfile", "default.model"))

DB_MODE = os.getenv('DRUCKER_DB_MODE', config.get('use.db', "sqlite"))
DB_MYSQL_HOST = os.getenv('DRUCKER_DB_MYSQL_HOST', config.get('db.mysql.host', ""))
DB_MYSQL_PORT = os.getenv('DRUCKER_DB_MYSQL_PORT', config.get('db.mysql.port', ""))
DB_MYSQL_DBNAME = os.getenv('DRUCKER_DB_MYSQL_DBNAME', config.get('db.mysql.dbname', ""))
DB_MYSQL_USER = os.getenv('DRUCKER_DB_MYSQL_USER', config.get('db.mysql.user', ""))
DB_MYSQL_PASSWORD = os.getenv('DRUCKER_DB_MYSQL_PASSWORD', config.get('db.mysql.password', ""))
