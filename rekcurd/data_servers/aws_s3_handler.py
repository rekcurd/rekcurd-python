# coding: utf-8


import boto3

from .data_handler import DataHandler
from rekcurd.utils import RekcurdConfig


class AwsS3Handler(DataHandler):
    """AwsS3Handler
    """
    def __init__(self, config: RekcurdConfig):
        super(AwsS3Handler, self).__init__(config)
        self._resource = boto3.resource(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
        )
        self._bucket = config.AWS_BUCKET_NAME

    def download(self, remote_filepath: str, local_filepath: str) -> None:
        self._resource.Bucket(self._bucket).download_file(remote_filepath, local_filepath)

    def upload(self, remote_filepath: str, local_filepath: str) -> None:
        self._resource.Bucket(self._bucket).upload_file(local_filepath, remote_filepath)
