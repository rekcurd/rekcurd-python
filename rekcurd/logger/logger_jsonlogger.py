#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
import time
from socket import gethostname

from pythonjsonlogger import jsonlogger

from rekcurd.utils import RekcurdConfig
from .logger_interface import SystemLoggerInterface, ServiceLoggerInterface


class JsonSystemLogger(SystemLoggerInterface):
    class JsonFormatter(jsonlogger.JsonFormatter):
        def parse(self):
            return [
                'host',
                'short_message',
                'timestamp',
                'level',
                'service',
                'ml_service',
                'service_level',
            ]

        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['host'] = gethostname()
            log_record['timestamp'] = int(time.time() * 1000) / 1000
            log_record['service'] = 'rekcurd'

    def __init__(self,
                 logger_name: str = 'rekcurd.system',
                 log_level: int = None,
                 config: RekcurdConfig = RekcurdConfig()) -> None:
        """
        Constructor
        :param logger_name:
        :param log_level:
        :param config: RekcurdConfig
        """
        self.config = config
        log_level = int(log_level or logging.DEBUG if config.DEBUG_MODE else logging.NOTSET)
        self.ml_service = config.APPLICATION_NAME
        self.service_level = config.SERVICE_LEVEL
        self.log = logging.getLogger(logger_name)
        handler = logging.StreamHandler()
        formatter = self.JsonFormatter()
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        self.log.handlers = []
        self.log.addHandler(handler)
        self.log.setLevel(log_level)

    def exception(self, message: str) -> None:
        """
        emits exception to log
        :param message: error message
        """
        self.log.error(message, exc_info=sys.exc_info(), stack_info=True,
                       extra={'short_message': message, 'level': 3,
                              'ml_service': self.ml_service,
                              'service_level': self.service_level})

    def error(self, message: str) -> None:
        """
        emits error log
        :param message: log
        """
        self.log.error(message, extra={'short_message': message, 'level': 3,
                                       'ml_service': self.ml_service,
                                       'service_level': self.service_level})

    def debug(self, message: str) -> None:
        """
        emits debug log
        :param message: log
        """
        self.log.debug(message, extra={'short_message': message, 'level': 7,
                                       'ml_service': self.ml_service,
                                       'service_level': self.service_level})

    def info(self, message: str) -> None:
        """
        emits info log
        :param message: log
        """
        self.log.info(message, extra={'short_message': message, 'level': 6,
                                      'ml_service': self.ml_service,
                                      'service_level': self.service_level})

    def warn(self, message: str) -> None:
        """
        emits warn log
        :param message: log
        """
        self.log.warning(message, extra={'short_message': message, 'level': 4,
                                         'ml_service': self.ml_service,
                                         'service_level': self.service_level})


class JsonServiceLogger(ServiceLoggerInterface):
    class JsonFormatter(jsonlogger.JsonFormatter):
        def parse(self):
            return [
                'host',
                'short_message',
                'timestamp',
                'level',
                'service',
                'ml_service',
                'service_level',
                'ml_input',
                'ml_output',
            ]

        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['host'] = gethostname()
            log_record['timestamp'] = int(time.time() * 1000) / 1000
            log_record['service'] = 'rekcurd'

    def __init__(self,
                 logger_name: str = 'rekcurd.service',
                 log_level: int = None,
                 config: RekcurdConfig = RekcurdConfig()):
        """
        Constructor
        :param logger_name:
        :param log_level:
        :param config: RekcurdConfig
        """
        self.logger_name = logger_name
        self.log_level = int(log_level or logging.DEBUG)
        self.config = config
        self.ml_service = config.APPLICATION_NAME
        self.service_level = config.SERVICE_LEVEL
        self.log = logging.getLogger(logger_name)
        handler = logging.StreamHandler()
        formatter = self.JsonFormatter()
        handler.setFormatter(formatter)
        handler.setLevel(self.log_level)
        self.log.addHandler(handler)
        self.log.setLevel(self.log_level)

    def emit(self, request, response, suppress_log_inout: bool = False) -> None:
        """
        emits service log
        """
        try:
            if suppress_log_inout:
                ml_input = ''
                ml_output = ''
            else:
                ml_input = super().to_str_from_request(request)
                ml_output = super().to_str_from_response(response)

            message = "prediction result."
            self.log.info(message, extra={'short_message': message,
                                          'level': 6, 'ml_service': self.ml_service,
                                          'service_level': self.service_level,
                                          'ml_input': ml_input,
                                          'ml_output': ml_output})
        except Exception:
            try:
                JsonSystemLogger(self.logger_name, self.log_level, self.config).exception("can't write log")
            except:
                pass
