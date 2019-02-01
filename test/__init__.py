import os

from rekcurd.logger import JsonServiceLogger, JsonSystemLogger
from test.dummy_app import DummyApp
import rekcurd.rekcurd_worker_servicer


os.environ["REKCURD_TEST_MODE"] = "True"
os.environ["REKCURD_SETTINGS_YAML"] = "test/test-settings.yml"

app = DummyApp()
service_logger = JsonServiceLogger(app.config)
system_logger = JsonSystemLogger(app.config)
Type = rekcurd.rekcurd_worker_servicer.RekcurdWorkerServicer.Type
