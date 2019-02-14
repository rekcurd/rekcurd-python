# coding: utf-8


from abc import ABCMeta, abstractmethod
from pathlib import Path

from rekcurd.utils import RekcurdConfig


def convert_to_valid_path(filepath: str) -> Path:
    """
    Remove a root path prefix "/", and a relative path "." and "..".
    :param filepath:
    :return:
    """
    valid_factors = [factor for factor in filepath.split("/") if factor and factor != ".."]
    return Path(*valid_factors)


class DataHandler(metaclass=ABCMeta):
    """Interface class.
    """
    LOCAL_MODEL_DIR: str = None
    MODEL_FILE_NAME: str = None
    LOCAL_EVAL_DIR: str = None

    def __init__(self, config: RekcurdConfig):
        valid_model_path = convert_to_valid_path(config.MODEL_FILE_PATH)
        self.LOCAL_MODEL_DIR = str(Path("rekcurd-model", valid_model_path.parent))
        self.MODEL_FILE_NAME = valid_model_path.name
        self.LOCAL_EVAL_DIR = "rekcurd-eval"

    @abstractmethod
    def download(self, remote_filepath: str, local_filepath: str) -> None:
        raise NotImplemented()

    @abstractmethod
    def upload(self, remote_filepath: str, local_filepath: str) -> None:
        raise NotImplemented()
