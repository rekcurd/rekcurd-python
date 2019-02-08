# coding: utf-8


import boto
import boto.s3.connection

from .data_handler import DataHandler
from rekcurd.utils import RekcurdConfig


class CephHandler(DataHandler):
    """CephHandler
    """
    def __init__(self, config: RekcurdConfig):
        super(CephHandler, self).__init__(config)
        self._conn = boto.connect_s3(
            aws_access_key_id=config.CEPH_ACCESS_KEY,
            aws_secret_access_key=config.CEPH_SECRET_KEY,
            host=config.CEPH_HOST,
            port=config.CEPH_PORT,
            is_secure=config.CEPH_IS_SECURE,
            calling_format=boto.s3.connection.OrdinaryCallingFormat())
        self._bucket = config.CEPH_BUCKET_NAME

    def download(self, remote_filepath: str, local_filepath: str) -> None:
        bucket = self._conn.get_bucket(self._bucket)
        key = bucket.get_key(remote_filepath)
        key.get_contents_to_filename(local_filepath)

    def upload(self, remote_filepath: str, local_filepath: str) -> None:
        bucket = self._conn.get_bucket(self._bucket)
        key = bucket.new_key(remote_filepath)
        key.set_contents_from_filename(local_filepath, replace=False)
