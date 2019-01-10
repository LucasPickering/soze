import redis
import signal

from . import logger
from .led import Led
from .lcd import Lcd
from .keepalive import Keepalive

# Potentially could read these from a config file
LED_CONFIG = {"hat_addr": 0x60, "pins": [3, 1, 2]}  # Pins are RGB
LCD_CONFIG = {"serial_port": "/dev/ttyAMA0"}


class SozeDisplay:
    def __init__(self, redis_url):
        redis_client = redis.from_url(redis_url)
        self._pubsub = redis_client.pubsub()

        self._keepalive = Keepalive(redis_client)
        self._resources = [
            self._keepalive,
            Led(redis_client=redis_client, pubsub=self._pubsub, **LED_CONFIG),
            Lcd(redis_client=redis_client, pubsub=self._pubsub, **LCD_CONFIG),
        ]
        self._threads = [self._keepalive]

        # Register exit handlers
        def stop_handler(sig, frame):
            self._stop()

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
            self._wait()
        finally:
            self._stop()  # Kill all threads
            # Tear down resources
            for res in self._resources:
                res.cleanup()
        logger.info("Stopped")

    def _wait(self):
        self._pubsub_thread.join()
        self._keepalive.join()

    def _stop(self):
        logger.info("Stopping...")
        self._keepalive.stop()
        self._pubsub_thread.stop()  # Will unsub from all channels
