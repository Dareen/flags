import os
import socket
import sys

from envparse import env

DEBUG = env("DEBUG", cast=bool, default=False)
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
APP_NAME = env("APP_NAME", default="flags")
ADMIN_MODE = env("ADMIN_MODE", cast=bool, default=False)
REDIS_ALL_FLAGS_KEY = env("REDIS_ALL_FLAGS_KEY", default="all_flags")

ZK_HOSTS = env("ZK_HOSTS",
               default="aws_zk1.dubizzlecloud.internal:2181,"
                       "aws_zk2.dubizzlecloud.internal:2181,"
                       "aws_zk3.dubizzlecloud.internal:2181,"
                       "aws_zk4.dubizzlecloud.internal:2181,"
                       "aws_zk5.dubizzlecloud.internal:2181")
# Time in seconds to wait for zookeeper connection to succeed.
ZK_CONNECTION_TIMEOUT = 5

HOST = "localhost"
PORT = 9595

PREFIX = env("PREFIX", default="flags")
VERSION = env("VERSION", default="v1")

REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env("REDIS_PORT", cast=int, default=6379)
REDIS_DB = env("REDIS_DB", cast=int, default=0)

#########################################
# Local Settings and Test Settings
###########
try:
    from flags.conf.local_settings import *
except ImportError:
    pass

try:
    from flags.conf.cis.test_settings import *
except ImportError:
    pass

#########################################
# Logging configuration
##########

LOGGING_DIR = "/var/log/dubizzle"

logging_formatters = {
    "standard": {
        "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
    },
    "syslog": {
        "format": "%(hostname)s %(appname)s %(levelname)s %(asctime)s %(module)s %(message)s"
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": logging_formatters,
    "filters": {
        APP_NAME: {
            "()": "%s.utils.customlogging.HostnameContextFilter" % APP_NAME,
            "hostname": socket.gethostname(),
            "appname": APP_NAME,
        },
    },
    "handlers": {
        "syslog": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.SysLogHandler",
            "facility": "local0",
            "formatter": "syslog",
            "address": [env("SYSLOG_HOST",
                            default="syslog-aws.dubizzlecloud.internal"),
                        env("SYSLOG_PORT", default=1122, cast=int)],
            "filters": ["hostname"],
        },
        "stdout_handler": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.__stdout__,
            "formatter": "standard",
        },
        "file_handler": {
            "level": LOG_LEVEL,
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGGING_DIR, "flags.log"),
            "formatter": "standard",
        }
    },
    "loggers": {
        "flags": {
            "handlers": ["stdout_handler", "file_handler", "syslog"],
            "level": LOG_LEVEL,
        },
        "kazoo.client": {
            "handlers": ["syslog"],
            "level": "INFO",
        },
    }
}
