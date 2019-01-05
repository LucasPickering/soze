#!/usr/bin/env python3

import argparse
import abc
import curses
import logging.config
import redis
import signal
import time
from threading import Event, Thread

from .color import BLACK, Color

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
                "filename": "display.log",
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
        self._pubsub.subscribe(**{sub_channel: self._on_pub})

        x, y, width, height = dimensions
        self._window = curses.newwin(height, width, y, x)

    @abc.abstractmethod
    def _on_pub(self, msg):
        pass


class Led(Resource):
    """
    @brief      A mocked version of the LED handler.
    """

    _COLOR_KEY = "reducer:led_color"

    def __init__(self, *args, **kwargs):
        super().__init__(
            dimensions=(0, 0, 50, 1), sub_channel="r2d:led", *args, **kwargs
        )
        self._set_color(BLACK)

    def _on_pub(self, msg):
        # Fetch the correct color from Redis and set it
        color = Color.from_bytes(self._redis.get(__class__._COLOR_KEY))
        self._set_color(color)

    def _set_color(self, color):
        curses_color = curses.color_pair(color.to_term_color())
        self._window.clear()
        self._window.addstr(f"LED Color: {color}", curses_color)
        self._window.noutrefresh()


class Keepalive(Thread):

    _KEEPALIVE_KEY = "reducer:keepalive"
    _KEEPALIVE_CHANNEL = "r2d:keepalive"

    def __init__(self, redis_client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis = redis_client
        self._shutdown = Event()

    @property
    def should_run(self):
        return not self._shutdown.is_set()

    def stop(self):
        self._shutdown.set()

    def run(self):
        logger.info("Keepalive started")
        while self.should_run:
            # Update
            self._redis.set(__class__._KEEPALIVE_KEY, b"\x01")
            self._redis.publish(__class__._KEEPALIVE_CHANNEL, b"")
            time.sleep(1)
        logger.info("Keepalive stopped")


class SozeDisplay:
    def __init__(self, redis_host):
        redis_client = redis.from_url(redis_host)
        self._pubsub = redis_client.pubsub()

        self._should_run = True
        self._keepalive = Keepalive(redis_client)
        Led(redis_client, self._pubsub)

        # Curses init
        curses.curs_set(0)  # Hide the cursor
        # Add xterm colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, curses.COLORS):
            curses.init_pair(i, i, -1)  # Background is always blank

        # Register exit handlers
        def stop_handler(sig, frame):
            self._stop()

        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)

    def run(self):
        logger.info("Starting...")
        try:
            # Start threads
            self._keepalive.start()
            self._pubsub_thread = self._pubsub.run_in_thread()

            # Constantly refresh curses, wait for Ctrl+c
            while self._should_run:
                curses.doupdate()
                time.sleep(0.01)
        finally:
            self._stop_threads()

    def _stop(self):
        logger.info("Stopping...")
        self._should_run = False

    def _stop_threads(self):
        self._pubsub_thread.stop()  # Will unsub from all channels
        self._keepalive.stop()


def main(stdscr):
    parser = argparse.ArgumentParser(
        description="Curses-based LED/LCD mock display"
    )
    parser.add_argument(
        "--redis",
        "-r",
        default="redis://localhost:6379",
        help="URL for the Redis host",
    )
    args = parser.parse_args()

    SozeDisplay(args.redis).run()
