import os
import redis
import signal

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

        # Register exit handlers
        def stop_handler(sig, frame):
            self._stop()

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
            self._wait()  # Block on child threads
        finally:
            # Stop all threads
            self._stop()

    def _wait(self):
        # Wait for PubSub to die (will be stopped by Ctrl+c)
        self._pubsub_thread.join()
        for res in self._resources:
            res.thread.join()

    def _stop(self):
        self._pubsub_thread.stop()  # This will unsub from all channels
        for res in self._resources:
            res.stop()


def main():
    s = SozeReducer(os.environ["REDIS_HOST"])
    s.run()
