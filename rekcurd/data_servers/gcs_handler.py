# coding: utf-8


import boto3

from .data_handler import DataHandler
from rekcurd.utils import RekcurdConfig


class GcsHandler(DataHandler):
    """GcsHandler
    """
    def __init__(self, config: RekcurdConfig):
        super(GcsHandler, self).__init__(config)
        self._resource = boto3.resource(
            's3',
            region_name="auto",
            endpoint_url="https://storage.googleapis.com",
            aws_access_key_id=config.GCS_ACCESS_KEY,
            aws_secret_access_key=config.GCS_SECRET_KEY,
        )
        self._bucket = config.GCS_BUCKET_NAME

    def download(self, remote_filepath: str, local_filepath: str) -> None:
        self._resource.Bucket(self._bucket).download_file(remote_filepath, local_filepath)

    def upload(self, remote_filepath: str, local_filepath: str) -> None:
        self._resource.Bucket(self._bucket).upload_file(local_filepath, remote_filepath)
