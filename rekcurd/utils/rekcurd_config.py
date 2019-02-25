# coding: utf-8


import os
import uuid
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
    __SERVICE_DEFAULT_HOST = "127.0.0.1"
    __SERVICE_DEFAULT_PORT = 5000
    __CEPH_DEFAULT_PORT = 8773
    KUBERNETES_MODE: str = None
    DEBUG_MODE: bool = None
    APPLICATION_NAME: str = None
    SERVICE_ID: str = None
    SERVICE_INSECURE_HOST: str = __SERVICE_DEFAULT_HOST
    SERVICE_INSECURE_PORT: int = __SERVICE_DEFAULT_PORT
    SERVICE_LEVEL: str = None
    MODEL_MODE_ENUM: ModelModeEnum = None
    MODEL_FILE_PATH: str = None
    CEPH_ACCESS_KEY: str = None
    CEPH_SECRET_KEY: str = None
    CEPH_HOST: str = None
    CEPH_PORT: int = __CEPH_DEFAULT_PORT
    CEPH_IS_SECURE: bool = None
    CEPH_BUCKET_NAME: str = None
    AWS_ACCESS_KEY: str = None
    AWS_SECRET_KEY: str = None
    AWS_BUCKET_NAME: str = None
    # TODO: GCS

    def __init__(self, config_file: str = None):
        self.KUBERNETES_MODE = os.getenv("REKCURD_KUBERNETES_MODE")
        if self.KUBERNETES_MODE is None:
            self.__load_from_file(config_file)
        else:
            self.__load_from_env()

    def set_configurations(
            self, debug_mode: bool = None, application_name: str = None,
            service_insecure_host: str = None, service_insecure_port: int = None,
            service_level: str = None, model_mode: str = None,
            model_filepath: str = None, ceph_access_key: str = None,
            ceph_secret_key: str = None, ceph_host: str = None,
            ceph_port: int = None, ceph_is_secure: bool = None,
            ceph_bucket_name: str = None, aws_access_key: str = None,
            aws_secret_key: str = None, aws_bucket_name: str = None,
            **options):
        self.DEBUG_MODE = debug_mode if debug_mode is not None else self.DEBUG_MODE
        self.APPLICATION_NAME = application_name or self.APPLICATION_NAME
        self.SERVICE_INSECURE_HOST = service_insecure_host or self.SERVICE_INSECURE_HOST
        self.SERVICE_INSECURE_PORT = int(service_insecure_port or self.SERVICE_INSECURE_PORT)
        self.SERVICE_LEVEL = service_level or self.SERVICE_LEVEL
        if model_mode is not None:
            self.MODEL_MODE_ENUM = ModelModeEnum.to_Enum(model_mode)
        self.MODEL_FILE_PATH = model_filepath or self.MODEL_FILE_PATH
        self.CEPH_ACCESS_KEY = ceph_access_key or self.CEPH_ACCESS_KEY
        self.CEPH_SECRET_KEY = ceph_secret_key or self.CEPH_SECRET_KEY
        self.CEPH_HOST = ceph_host or self.CEPH_HOST
        self.CEPH_PORT = int(ceph_port or self.CEPH_PORT)
        self.CEPH_IS_SECURE = ceph_is_secure if ceph_is_secure is not None else self.CEPH_IS_SECURE
        self.CEPH_BUCKET_NAME = ceph_bucket_name or self.CEPH_BUCKET_NAME
        self.AWS_ACCESS_KEY = aws_access_key or self.AWS_ACCESS_KEY
        self.AWS_SECRET_KEY = aws_secret_key or self.AWS_SECRET_KEY
        self.AWS_BUCKET_NAME = aws_bucket_name or self.AWS_BUCKET_NAME
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
        self.SERVICE_ID = uuid.uuid4().hex
        self.SERVICE_INSECURE_HOST = config_app.get("host", self.__SERVICE_DEFAULT_HOST)
        self.SERVICE_INSECURE_PORT = config_app.get("port", self.__SERVICE_DEFAULT_PORT)
        self.SERVICE_LEVEL = config_app.get("service_level", "development")
        config_model = config.get("model", dict())
        model_mode = config_model.get("mode", "local")
        self.MODEL_MODE_ENUM = ModelModeEnum.to_Enum(model_mode)
        if self.MODEL_MODE_ENUM == ModelModeEnum.LOCAL:
            config_model_mode = config_model.get(model_mode, dict())
            self.MODEL_FILE_PATH = config_model_mode.get("filepath", "model/default.model")
        elif self.MODEL_MODE_ENUM == ModelModeEnum.CEPH_S3:
            config_model_mode = config_model.get(model_mode, dict())
            self.MODEL_FILE_PATH = config_model_mode.get("filepath", "model/default.model")
            self.CEPH_ACCESS_KEY = config_model_mode.get("access_key")
            self.CEPH_SECRET_KEY = config_model_mode.get("secret_key")
            self.CEPH_HOST = config_model_mode.get("host")
            self.CEPH_PORT = config_model_mode.get("port", self.__CEPH_DEFAULT_PORT)
            self.CEPH_IS_SECURE = config_model_mode.get("is_secure", False)
            self.CEPH_BUCKET_NAME = config_model_mode.get("bucket")
        elif self.MODEL_MODE_ENUM == ModelModeEnum.AWS_S3:
            config_model_mode = config_model.get(model_mode, dict())
            self.MODEL_FILE_PATH = config_model_mode.get("filepath", "model/default.model")
            self.AWS_ACCESS_KEY = config_model_mode.get("access_key")
            self.AWS_SECRET_KEY = config_model_mode.get("secret_key")
            self.AWS_BUCKET_NAME = config_model_mode.get("bucket")
        else:
            # TODO: GCS
            raise ValueError("'{}' is not supported as ModelModeEnum".format(model_mode))

    def __load_from_env(self):
        self.DEBUG_MODE = os.getenv("REKCURD_DEBUG_MODE", "True").lower() == 'true'
        self.APPLICATION_NAME = os.getenv("REKCURD_APPLICATION_NAME")
        self.SERVICE_ID = os.getenv("REKCURD_SERVICE_ID")
        self.SERVICE_INSECURE_HOST = os.getenv("REKCURD_SERVICE_INSECURE_HOST", self.__SERVICE_DEFAULT_HOST)
        self.SERVICE_INSECURE_PORT = int(os.getenv("REKCURD_SERVICE_INSECURE_PORT", self.__SERVICE_DEFAULT_PORT))
        self.SERVICE_LEVEL = os.getenv("REKCURD_SERVICE_LEVEL")
        model_mode = os.getenv("REKCURD_MODEL_MODE")
        self.MODEL_MODE_ENUM = ModelModeEnum.to_Enum(model_mode)
        self.MODEL_FILE_PATH = os.getenv("REKCURD_MODEL_FILE_PATH")
        self.CEPH_ACCESS_KEY = os.getenv("REKCURD_CEPH_ACCESS_KEY")
        self.CEPH_SECRET_KEY = os.getenv("REKCURD_CEPH_SECRET_KEY")
        self.CEPH_HOST = os.getenv("REKCURD_CEPH_HOST")
        self.CEPH_PORT = int(os.getenv("REKCURD_CEPH_PORT", str(self.__CEPH_DEFAULT_PORT)))
        self.CEPH_IS_SECURE = os.getenv("REKCURD_CEPH_IS_SECURE", "False").lower() == 'true'
        self.CEPH_BUCKET_NAME = os.getenv("REKCURD_CEPH_BUCKET_NAME")
        self.AWS_ACCESS_KEY = os.getenv("REKCURD_AWS_ACCESS_KEY")
        self.AWS_SECRET_KEY = os.getenv("REKCURD_AWS_SECRET_KEY")
        self.AWS_BUCKET_NAME = os.getenv("REKCURD_AWS_BUCKET_NAME")
        # TODO: GCS
