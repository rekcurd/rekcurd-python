#!/usr/bin/python
# -*- coding: utf-8 -*-

from concurrent import futures
import grpc
import drucker_pb2_grpc
import time

from drucker.core.drucker_dashboard_servicer import DruckerDashboardServicer
from drucker.core.drucker_worker_servicer import DruckerWorkerServicer
from drucker.logger.logger_jsonlogger import SystemLogger, ServiceLogger
from predict import Predict
from drucker.utils.env_loader import SERVICE_LEVEL_ENUM, APPLICATION_NAME, SERVICE_PORT

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def serve():
    system_logger = SystemLogger(logger_name="drucker", app_name=APPLICATION_NAME, app_env=SERVICE_LEVEL_ENUM)
    service_logger = ServiceLogger(app_name=APPLICATION_NAME, app_env=SERVICE_LEVEL_ENUM)
    predictor = Predict()
    system_logger.info("Wake-up drucker worker.")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    drucker_pb2_grpc.add_DruckerDashboardServicer_to_server(
        DruckerDashboardServicer(logger=system_logger, predictor=predictor), server)
    drucker_pb2_grpc.add_DruckerWorkerServicer_to_server(
        DruckerWorkerServicer(logger=service_logger, predictor=predictor), server)
    server.add_insecure_port("[::]:{0}".format(SERVICE_PORT))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        system_logger.info("Shutdown drucker worker.")
        server.stop(0)


if __name__ == '__main__':
    serve()
