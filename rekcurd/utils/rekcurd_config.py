# coding: utf-8


import os
import yaml

from enum import Enum


class ModelModeEnum(Enum):
    """
    Rekcurd model storage options.
    """
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


class RekcurdConfig:
    """
    Rekcurd configurations.
    """
    KUBERNETES_MODE: str = None
    DEBUG_MODE: bool = None
    APPLICATION_NAME: str = None
    SERVICE_NAME: str = None
    SERVICE_PORT: int = None
    SERVICE_LEVEL: str = None
    MODEL_MODE_ENUM: ModelModeEnum = None
    MODEL_FILE_PATH: str = None
    CEPH_ACCESS_KEY: str = None
    CEPH_SECRET_KEY: str = None
    CEPH_HOST: str = None
    CEPH_PORT: int = None
    CEPH_IS_SECURE: bool = None
    CEPH_BUCKET_NAME: str = None
    # TODO: AWS
    # TODO: GCS

    def __init__(self, config_file: str = None):
        self.KUBERNETES_MODE = os.getenv("REKCURD_KUBERNETES_MODE")
        if self.KUBERNETES_MODE is None:
            self.__load_from_file(config_file)
        else:
            self.__load_from_env()

    def set_configurations(
            self, debug_mode: bool = None,
            application_name: str = None, service_port: int = None,
            service_level: str = None, model_mode: str = None,
            model_filepath: str = None, ceph_access_key: str = None,
            ceph_secret_key: str = None, ceph_host: str = None,
            ceph_port: int = None, ceph_is_secure: bool = None,
            ceph_bucket_name: str = None,
            **options):
        self.DEBUG_MODE = bool(debug_mode or self.DEBUG_MODE)
        self.APPLICATION_NAME = application_name or self.APPLICATION_NAME
        self.SERVICE_NAME = self.APPLICATION_NAME
        self.SERVICE_PORT = int(service_port or self.SERVICE_PORT)
        self.SERVICE_LEVEL = service_level or self.SERVICE_LEVEL
        if model_mode is not None:
            self.MODEL_MODE_ENUM = ModelModeEnum.to_Enum(model_mode)
        self.MODEL_FILE_PATH = model_filepath or self.MODEL_FILE_PATH
        self.CEPH_ACCESS_KEY = ceph_access_key or self.CEPH_ACCESS_KEY
        self.CEPH_SECRET_KEY = ceph_secret_key or self.CEPH_SECRET_KEY
        self.CEPH_HOST = ceph_host or self.CEPH_HOST
        self.CEPH_PORT = int(ceph_port or self.CEPH_PORT)
        self.CEPH_IS_SECURE = bool(ceph_is_secure or self.CEPH_IS_SECURE)
        self.CEPH_BUCKET_NAME = ceph_bucket_name or self.CEPH_BUCKET_NAME
        # TODO: AWS
        # TODO: GCS

    def __load_from_file(self, config_file: str):
        if config_file is not None:
            with open(config_file, 'r') as f:
                config = yaml.load(f)
        else:
            config = dict()
        self.DEBUG_MODE = config.get("debug", True)
        config_app = config.get("app", dict())
        self.APPLICATION_NAME = config_app.get("name", "sample")
        self.SERVICE_NAME = self.APPLICATION_NAME
        self.SERVICE_PORT = config_app.get("port", 5000)
        self.SERVICE_LEVEL = config_app.get("service_level", "development")
        config_model = config.get("model", dict())
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
        self.DEBUG_MODE = os.getenv("REKCURD_DEBUG_MODE", "True").lower() == 'true'
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
