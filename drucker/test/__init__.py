import os

from drucker.logger import JsonServiceLogger, JsonSystemLogger
from drucker.test.dummy_app import DummyApp
import drucker.drucker_worker_servicer


os.environ["DRUCKER_TEST_MODE"] = "True"
os.environ["DRUCKER_SETTINGS_YAML"] = "drucker/test/test-settings.yml"

app = DummyApp()
service_logger = JsonServiceLogger(app.config)
system_logger = JsonSystemLogger(app.config)
Type = drucker.drucker_worker_servicer.DruckerWorkerServicer.Type
