# coding: utf-8


import pickle

from pathlib import Path
from typing import Iterator

from rekcurd.protobuf import rekcurd_pb2
from rekcurd.utils import RekcurdConfig, ModelModeEnum
from .data_handler import DataHandler, convert_to_valid_path
from .local_handler import LocalHandler
from .ceph_handler import CephHandler
from .aws_s3_handler import AwsS3Handler


class DataServer(object):
    """DataServer
    Return file path. Download files if needed.
    """

    # Suffix for evaluation results
    __EVALUATE_RESULT = '_eval_res.pkl'
    __EVALUATE_DETAIL = '_eval_detail.pkl'

    def __init__(self, config: RekcurdConfig):
        self.config = config
        if config.MODEL_MODE_ENUM == ModelModeEnum.LOCAL:
            self._api_handler = LocalHandler(config)
        elif config.MODEL_MODE_ENUM == ModelModeEnum.CEPH_S3:
            self._api_handler = CephHandler(config)
        elif config.MODEL_MODE_ENUM == ModelModeEnum.AWS_S3:
            self._api_handler = AwsS3Handler(config)
        else:
            raise ValueError("Invalid ModelModeEnum value.")

    def get_model_path(self) -> str:
        local_filepath = Path(self._api_handler.LOCAL_MODEL_DIR, self._api_handler.MODEL_FILE_NAME)
        if not local_filepath.exists():
            local_filepath.parent.mkdir(parents=True, exist_ok=True)
            self._api_handler.download(self.config.MODEL_FILE_PATH, str(local_filepath))
        return str(local_filepath)

    def switch_model(self, filepath: str) -> str:
        valid_path = convert_to_valid_path(filepath)
        if filepath != str(valid_path):
            raise Exception(f'Error: Invalid file path specified -> {filepath}')

        local_filepath = Path(self._api_handler.LOCAL_MODEL_DIR, valid_path.name)
        if not local_filepath.exists():
            local_filepath.parent.mkdir(parents=True, exist_ok=True)
            self._api_handler.download(filepath, str(local_filepath))
        self._api_handler.MODEL_FILE_NAME = valid_path.name
        return str(local_filepath)

    def upload_model(self, request_iterator: Iterator[rekcurd_pb2.UploadModelRequest]) -> str:
        first_req = next(request_iterator)
        filepath = first_req.path
        valid_path = convert_to_valid_path(filepath)
        if filepath != str(valid_path):
            raise Exception(f'Error: Invalid file path specified -> {filepath}')

        local_filepath = Path(self._api_handler.LOCAL_MODEL_DIR, valid_path.name)
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        with local_filepath.open(mode='wb') as f:
            f.write(first_req.data)
            for request in request_iterator:
                f.write(request.data)
            del first_req
        self._api_handler.upload(filepath, str(local_filepath))
        return str(local_filepath)

    def get_evaluation_data_path(self, filepath: str) -> str:
        valid_path = convert_to_valid_path(filepath)
        if filepath != str(valid_path):
            raise Exception(f'Error: Invalid file path specified -> {filepath}')

        local_filepath = Path(self._api_handler.LOCAL_EVAL_DIR, valid_path.name)
        if not local_filepath.exists():
            local_filepath.parent.mkdir(parents=True, exist_ok=True)
            self._api_handler.download(filepath, str(local_filepath))
        return str(local_filepath)

    def _get_eval_result(self, filepath: str, suffix: str):
        valid_path = convert_to_valid_path(filepath)
        if filepath != str(valid_path):
            raise Exception(f'Error: Invalid file path specified -> {filepath}')

        local_filepath = Path(self._api_handler.LOCAL_EVAL_DIR, valid_path.name+suffix)
        if not local_filepath.exists():
            local_filepath.parent.mkdir(parents=True, exist_ok=True)
            self._api_handler.download(filepath+suffix, str(local_filepath))
        return str(local_filepath)

    def get_eval_result_summary(self, filepath: str) -> str:
        return self._get_eval_result(filepath, self.__EVALUATE_RESULT)

    def get_eval_result_detail(self, filepath: str) -> str:
        return self._get_eval_result(filepath, self.__EVALUATE_DETAIL)

    def upload_evaluation_data(self, request_iterator: Iterator[rekcurd_pb2.UploadEvaluationDataRequest]) -> str:
        first_req = next(request_iterator)
        filepath = first_req.data_path
        valid_path = convert_to_valid_path(filepath)
        if filepath != str(valid_path):
            raise Exception(f'Error: Invalid evaluation file path specified -> {filepath}')

        local_filepath = Path(self._api_handler.LOCAL_EVAL_DIR, valid_path.name)
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        with local_filepath.open(mode='wb') as f:
            f.write(first_req.data)
            for request in request_iterator:
                f.write(request.data)
            del first_req
        self._api_handler.upload(filepath, str(local_filepath))
        return str(local_filepath)

    def _upload_evaluation_result(self, data: object, filepath: str, suffix: str):
        valid_path = convert_to_valid_path(filepath)
        if filepath != str(valid_path):
            raise Exception(f'Error: Invalid evaluation result file path specified -> {filepath}')
        local_filepath = Path(self._api_handler.LOCAL_EVAL_DIR, valid_path.name+suffix)
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        with local_filepath.open(mode='wb') as f:
            pickle.dump(data, f)
        self._api_handler.upload(filepath+suffix, str(local_filepath))
        return str(local_filepath)

    def upload_evaluation_result_summary(self, data: object, filepath: str) -> str:
        return self._upload_evaluation_result(data, filepath, self.__EVALUATE_RESULT)

    def upload_evaluation_result_detail(self, data: object, filepath: str) -> str:
        return self._upload_evaluation_result(data, filepath, self.__EVALUATE_DETAIL)
