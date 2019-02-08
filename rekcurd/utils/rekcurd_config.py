# coding: utf-8


import os
import yaml

from enum import Enum


class RekcurdConfig:
    def __init__(self, config_file: str):
        self.KUBERNETES_MODE = os.getenv("REKCURD_KUBERNETES_MODE")
        if self.KUBERNETES_MODE is None:
            self.__load_from_file(config_file)
        else:
            self.__load_from_env()

    def __load_from_file(self, config_file: str):
        with open(config_file, 'r') as f:
            config = yaml.load(f)
        self.TEST_MODE = config.get("test", True)
        config_app = config.get("app")
        self.APPLICATION_NAME = config_app.get("name")
        self.SERVICE_NAME = self.APPLICATION_NAME
        self.SERVICE_PORT = config_app.get("port", 5000)
        self.SERVICE_LEVEL = config_app.get("service_level", "development")
        config_model = config.get("model")
        model_mode = config_model.get("mode", "local")
        self.MODEL_MODE_ENUM = ModelModeEnum.to_Enum(model_mode)
        self.MODEL_FILE_PATH = config_model.get("filepath", "./model/default.model")
        config_ceph = config.get("ceph", dict())
        self.CEPH_ACCESS_KEY = config_ceph.get("access_key")
        self.CEPH_SECRET_KEY = config_ceph.get("secret_key")
        self.CEPH_HOST = config_ceph.get("host")
        self.CEPH_PORT = config_ceph.get("port", 8773)
        self.CEPH_IS_SECURE = config_ceph.get("is_secure", False)
        self.CEPH_BUCKET_NAME = config_ceph.get("bucket")
        # TODO: AWS
        # TODO: GCS

    def __load_from_env(self):
        self.TEST_MODE = os.getenv("REKCURD_TEST_MODE", "True").lower() == 'true'
        self.APPLICATION_NAME = os.getenv("REKCURD_APPLICATION_NAME")
        self.SERVICE_NAME = os.getenv("REKCURD_SERVICE_NAME")
        self.SERVICE_PORT = int(os.getenv("REKCURD_SERVICE_PORT"))
        self.SERVICE_LEVEL = os.getenv("REKCURD_SERVICE_LEVEL")
        model_mode = os.getenv("REKCURD_MODEL_MODE")
        self.MODEL_MODE_ENUM = ModelModeEnum.to_Enum(model_mode)
        self.MODEL_FILE_PATH = os.getenv("REKCURD_MODEL_FILE_PATH")
        self.CEPH_ACCESS_KEY = os.getenv("REKCURD_CEPH_ACCESS_KEY")
        self.CEPH_SECRET_KEY = os.getenv("REKCURD_CEPH_SECRET_KEY")
        self.CEPH_HOST = os.getenv("REKCURD_CEPH_HOST")
        self.CEPH_PORT = int(os.getenv("REKCURD_CEPH_PORT"))
        self.CEPH_IS_SECURE = os.getenv("REKCURD_CEPH_IS_SECURE").lower() == 'true'
        self.CEPH_BUCKET_NAME = os.getenv("REKCURD_CEPH_BUCKET_NAME")
        # TODO: AWS
        # TODO: GCS


class ModelModeEnum(Enum):
    LOCAL = 'local'
    CEPH_S3 = 'ceph_s3'
    AWS_S3 = 'aws_s3'
    GCS = 'gcs'

    @classmethod
    def to_Enum(cls, mode: str):
        if cls.LOCAL.value == mode:
            return cls.LOCAL
        elif cls.CEPH_S3.value == mode:
            return cls.CEPH_S3
        elif cls.AWS_S3.value == mode:
            return cls.AWS_S3
        elif cls.GCS.value == mode:
            return cls.GCS
        else:
            raise ValueError("'{}' is not supported as ModelModeEnum".format(mode))
