# coding: utf-8


from pathlib import Path

from .data_handler import DataHandler
from rekcurd.utils import RekcurdConfig


class LocalHandler(DataHandler):
    """LocalHandler
    """
    def __init__(self, config: RekcurdConfig):
        super(LocalHandler, self).__init__(config)
        # Overwrite: No additional local directory is needed.
        self.LOCAL_MODEL_DIR = str(Path(config.MODEL_FILE_PATH).parent)

    def download(self, remote_filepath: str, local_filepath: str) -> None:
        raise Exception(
            "Error: No such a file. Local mode requires to store"
            " a ML model file on the directory you specified. "
            "-> \"{}\"".format(local_filepath))

    def upload(self, remote_filepath: str, local_filepath: str) -> None:
        pass
