#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
import time
from socket import gethostname

from fluent import handler, sender

from rekcurd.utils import RekcurdConfig
from .logger_interface import SystemLoggerInterface, ServiceLoggerInterface


class FluentSystemLogger(SystemLoggerInterface):

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
        application_name = config.APPLICATION_NAME
        service_level = config.SERVICE_LEVEL
        self.log = logging.getLogger(logger_name)
        self.log.setLevel(log_level)
        self.log.handlers = []
        self.log.addHandler(self.__init_fluent_handler(application_name, service_level, log_level))

    def __init_fluent_handler(self, application_name: str, service_level: str, log_level: int):
        custom_format = {
            'host': gethostname(),
            'short_message': '%(message)s',
            'timestamp': '%(created)d.%(msecs)d',
            'level': '%(loglevel)d',
            'service': 'rekcurd',
            'ml_service': application_name,
            'service_level': service_level
        }
        fluent_handler = handler.FluentHandler('rekcurd')
        formatter = handler.FluentRecordFormatter(custom_format)
        fluent_handler.setFormatter(formatter)
        fluent_handler.setLevel(log_level)
        return fluent_handler

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


class FluentServiceLogger(ServiceLoggerInterface):

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
        self.logger = sender.FluentSender(logger_name)

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
                'level': self.log_level,
                'service': 'rekcurd',
                'ml_service': self.ml_service,
                'service_level': self.service_level,
                'ml_input': ml_input,
                'ml_output': ml_output
            })
        except:
            try:
                FluentSystemLogger(self.logger_name, self.log_level, self.config).exception("can't write log")
            except:
                pass
