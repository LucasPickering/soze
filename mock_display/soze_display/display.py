#!/usr/bin/env python3

import argparse
import abc
import curses
import logging.config
import redis
import time

from .color import Color

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "f": {
                "format": "{asctime} [{threadName} {levelname}] {message}",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{",
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "formatter": "f",
                "filename": "gui.log",
                "mode": "w",
            }
        },
        "loggers": {__name__: {"handlers": ["file"], "level": "DEBUG"}},
    }
)
logger = logging.getLogger(__name__)


class Resource:
    def __init__(self, redis_client, pubsub, dimensions, sub_channel):
        self._redis = redis_client
        self._pubsub = pubsub
        self._sub_channel = sub_channel
        self._pubsub.subscribe(**{self._sub_channel: self._on_pub})

        x, y, width, height = dimensions
        self._window = curses.newwin(height, width, y, x)

    @property
    def sub_channel(self):
        return self._sub_channel

    @abc.abstractmethod
    def _on_pub(self, msg):
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Curses-based mock LED/LCD display"
    )
    parser.add_argument(
        "--redis",
        "-r",
        default="redis://localhost:6379",
        help="URL for the Redis host",
    )
    args = parser.parse_args()

    print(args)
