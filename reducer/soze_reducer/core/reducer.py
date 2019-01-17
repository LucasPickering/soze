import redis
import signal
import time

from soze_reducer import logger
from soze_reducer.led.led import Led
from soze_reducer.lcd.lcd import Lcd
from .keepalive import Keepalive


class SozeReducer:
    def __init__(self, redis_url):
        self._redis = redis.from_url(redis_url)
        self._pubsub = self._redis.pubsub()
        self._pubsub_thread = None  # Will be populated during run

        self._keepalive = Keepalive(
            redis_client=self._redis, pubsub=self._pubsub
        )
        self._resources = [
            Led(
                redis_client=self._redis,
                pubsub=self._pubsub,
                keepalive=self._keepalive,
            ),
            Lcd(
                redis_client=self._redis,
                pubsub=self._pubsub,
                keepalive=self._keepalive,
            ),
        ]
        self._should_run = True

        # Register exit handlers
        def stop_handler(sig, frame):
            self._should_run = False

        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)

    def run(self):
        # Start the helper threads
        try:
            # One thread to listen for Redis pubs, and one thread for each
            # resource to periodically compute derived state
            self._pubsub_thread = self._pubsub.run_in_thread()
            for res in self._resources:
                res.thread.start()
            logger.info("Started threads")

            # Thread.join blocks signals so we need this loop
            while self._should_run:
                time.sleep(1)
        finally:
            # Stop all threads
            self._stop()

    def _stop(self):
        self._pubsub_thread.stop()  # This will unsub from all channels
        for res in self._resources:
            res.stop()
