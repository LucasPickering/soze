import redis

from .led import Led
from .lcd import Lcd
from .keepalive import Keepalive

MOTOR_HAT_ADDR = 0x60
MOTOR_HAT_PINS = [3, 1, 2]  # RGB
LCD_SERIAL_PORT = "/dev/ttyAMA0"


class SozeDisplay:
    def __init__(self, redis_url):
        redis_client = redis.from_url(redis_url)
        self._pubsub = redis_client.pubsub()

        self._keepalive = Keepalive(redis_client)
        self._resources = [
            Led(redis_client, self._pubsub),
            Lcd(redis_client, self._pubsub),
        ]

    def _init_resources(self, cfg):
        return [
            Led(**cfg["led"]),
            Lcd(**cfg["lcd"]),
            Keepalive(**cfg["keepalive"]),
        ]

    def run(self):
        for res in self._resources:
            res.init()
        try:
            pubsub_thread = self._pubsub.run_in_thread()
            pubsub_thread.join()
        finally:
            for res in self._resources:
                res.cleanup()
