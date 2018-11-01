#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import pathlib


root_path = pathlib.Path(os.path.abspath(__file__)).parent.parent
sys.path.append(str(root_path))


from concurrent import futures
import grpc
import time

from drucker import DruckerDashboardServicer, DruckerWorkerServicer
from drucker.logger import JsonSystemLogger, JsonServiceLogger
from drucker.protobuf import drucker_pb2_grpc
from template.app import MyApp

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def serve():
    app = MyApp("./settings.yml")
    system_logger = JsonSystemLogger(app.config)
    service_logger = JsonServiceLogger(app.config)
    system_logger.info("Wake-up drucker worker.")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    drucker_pb2_grpc.add_DruckerDashboardServicer_to_server(
        DruckerDashboardServicer(logger=system_logger, app=app), server)
    drucker_pb2_grpc.add_DruckerWorkerServicer_to_server(
        DruckerWorkerServicer(logger=service_logger, app=app), server)
    server.add_insecure_port("[::]:{0}".format(app.config.SERVICE_PORT))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        system_logger.info("Shutdown drucker worker.")
        server.stop(0)


if __name__ == '__main__':
    serve()
