import redis
import signal
import time

from . import logger
from .led import Led
from .lcd import Lcd
from .keepalive import Keepalive

# Potentially could read these from a config file
KEEPALIVE_CONFIG = {"pin": 4}
LED_CONFIG = {"hat_addr": 0x60, "pins": [3, 1, 2]}  # Pins are RGB
LCD_CONFIG = {"serial_port": "/dev/ttyAMA0"}


class SozeDisplay:
    def __init__(self, redis_url):
        redis_client = redis.from_url(redis_url)
        self._pubsub = redis_client.pubsub()

        self._keepalive = Keepalive(redis_client, **KEEPALIVE_CONFIG)
        self._resources = [
            self._keepalive,
            Led(redis_client=redis_client, pubsub=self._pubsub, **LED_CONFIG),
            Lcd(redis_client=redis_client, pubsub=self._pubsub, **LCD_CONFIG),
        ]
        self._threads = [self._keepalive]
        self._should_run = True

        # Register exit handlers
        def stop_handler(sig, frame):
            self._should_run = False

        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)

    def run(self):
        logger.info("Starting...")
        for res in self._resources:
            res.init()
        try:
            # Start threads
            self._keepalive.start()
            self._pubsub_thread = self._pubsub.run_in_thread()

            # Thread.join blocks signals so we need this loop
            while self._should_run:
                time.sleep(1)
        finally:
            self._stop()
            self._cleanup()
            logger.info("Stopped")

    def _stop(self):
        logger.info("Stopping...")
        self._keepalive.stop()
        self._pubsub_thread.stop()  # Will unsub from all channels

    def _cleanup(self):
        logger.info("Cleaning up...")
        for res in self._resources:
            res.cleanup()
