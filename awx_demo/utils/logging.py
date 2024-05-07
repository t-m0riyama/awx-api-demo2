# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging


class Logging(object):
    # const
    FLET_LOGGER_NAME = 'flet_core'

    @classmethod
    def init(cls, log_dir, log_file, log_level):
        logging.basicConfig(
            filename='{}/{}'.format(log_dir, log_file),
            format="\"%(asctime)s\"\t%(levelname)s\t%(message)s",
            datefmt='%Y/%m/%d %H:%M:%S',
            level=log_level,
        )

    @classmethod
    def get_logger(cls):
        logger = logging.getLogger(Logging.FLET_LOGGER_NAME)
        return logger

    @classmethod
    def info(cls, message):
        Logging.get_logger().info(message)

    @classmethod
    def warning(cls, message):
        Logging.get_logger().warning(message)

    @classmethod
    def error(cls, message):
        Logging.get_logger().error(message)

    @classmethod
    def debug(cls, message):
        Logging.get_logger().debug(message)
