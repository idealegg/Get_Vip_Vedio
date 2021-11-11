# -*- coding: utf-8 -*-

import json
import logging.config
import os
import functools
import sys


logger = logging.getLogger()
logger_names = ['root']
conf_dir = 'Conf'
conf_file = 'logging.json'
conf_path = os.path.join(conf_dir, conf_file)
log_dir = 'Logs'


def setup_logging(prefix=None, default_path=conf_path, default_level=logging.INFO, env_key="LOG_CFG"):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "r") as f:
            config = json.load(f)
            if not prefix:
                prefix = os.path.basename(os.path.splitext(sys.argv[0])[0])
            config['handlers']['info_file_handler']['filename'] = os.path.join(log_dir, "%s_info.log" % prefix)
            config['handlers']['error_file_handler']['filename'] = os.path.join(log_dir, "%s_error.log" % prefix)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def log(cls_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            global logger
            global logger_names
            logger.debug('call %s():' % func.__name__)
            log_name = "%s.%s" % (cls_name, func.__name__)
            logger_names.append(log_name)
            logger = logging.getLogger(log_name)
            ret = func(*args, **kw)
            logger.debug('exit %s():' % logger_names.pop())
            logger = logging.getLogger(logger_names[-1])
            logger.debug('back %s():' % logger_names[-1])
            return ret
        return wrapper
    return decorator


if __name__ == "__main__":
    setup_logging()

    @log('Test')
    def aaaa():
        logger.info("2 ")
        logger.info(logger_names)

    @log('Test')
    def aa():
        logger.info("1 in")
        logger.info(logger_names)
        aaaa()
        logger.info(logger_names)
        logger.info('1 out')
    setup_logging()
    aa()

