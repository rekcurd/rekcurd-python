#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
import time
from socket import gethostname

from fluent import handler, sender

from logger.logger_interface import SystemLoggerInterface, ServiceLoggerInterface
from utils.env_loader import ServiceEnvType, SERVICE_LEVEL_ENUM, APPLICATION_NAME


class SystemLogger(SystemLoggerInterface):

    def __init__(self, logger_name: str = 'drucker',
                 log_level: int = logging.NOTSET, app_name: str = APPLICATION_NAME,
                 app_env: ServiceEnvType = ServiceEnvType.DEVELOPMENT) -> None:
        """
        constructor
        :param logger_name:
        :param log_level:
        :param app_name:
        :param app_env:
        """
        super().__init__()
        self.log = logging.getLogger(logger_name)
        self.log.setLevel(log_level)

        custom_format = {
            'host': gethostname(),
            'short_message': '%(message)s',
            'timestamp': '%(created)d.%(msecs)d',
            'level': '%(loglevel)d',
            'service': 'drucker',
            'ml_service': app_name,
            'service_level': app_env
        }

        fluent_handler = handler.FluentHandler('drucker')
        formatter = handler.FluentRecordFormatter(custom_format)
        fluent_handler.setFormatter(formatter)
        fluent_handler.setLevel(log_level)
        self.log.addHandler(fluent_handler)

    def exception(self, message: str) -> None:
        """
        emits exception to log
        :param message: error message
        """
        self.log.error(message, exc_info=sys.exc_info(), stack_info=True, extra={'loglevel': 3})

    def error(self, message: str) -> None:
        """
        emits error log
        :param message: log
        """
        self.log.error(message, extra={'loglevel': 3})

    def debug(self, message: str) -> None:
        """
        emits debug log
        :param message: log
        """
        self.log.debug(message, extra={'loglevel': 7})

    def info(self, message: str) -> None:
        """
        emits info log
        :param message: log
        """
        self.log.info(message, extra={'loglevel': 6})

    def warn(self, message: str) -> None:
        """
        emits warn log
        :param message: log
        """
        self.log.warning(message, extra={'loglevel': 4})


class ServiceLogger(ServiceLoggerInterface):

    def __init__(self, app_name: str = APPLICATION_NAME,
                 app_env: ServiceEnvType = ServiceEnvType.DEVELOPMENT):
        """
        constructor
        :param app_name:
        :param app_env:
        """
        super().__init__()
        self.logger = sender.FluentSender('drucker_service')
        self.ml_service = app_name
        self.service_level = app_env

    def emit(self, request, response, suppress_log_inout: bool = False) -> None:
        """
        emits service log
        :param request:
        :param response:
        :param suppress_log_inout:
        :return:
        """
        try:
            if suppress_log_inout:
                ml_input = ''
                ml_output = ''
            else:
                ml_input = super().to_str_from_request(request)
                ml_output = super().to_str_from_response(response)

            self.logger.emit(None, {
                'host': gethostname(),
                'short_message': 'prediction result.',
                'timestamp': int(time.time() * 1000) / 1000,
                'level': logging.INFO,
                'service': 'drucker',
                'ml_service': self.ml_service,
                'service_level': self.service_level,
                'ml_input': ml_input,
                'ml_output': ml_output
            })
        except:
            try:
                SystemLogger(logger_name="ServiceLogger", app_name=APPLICATION_NAME,
                             app_env=SERVICE_LEVEL_ENUM).exception("can't write log")
            except:
                pass
