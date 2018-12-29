import struct

from soze_reducer import logger
from .resource import RedisSubscriber


class Keepalive(RedisSubscriber):

    _KEEPALIVE_KEY = "reducer:keepalive"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, sub_channel="r2d:keepalive", **kwargs)
        self._alive = False

    @property
    def is_alive(self):
        return self._alive

    def _on_pub(self, msg):
        is_alive = struct.unpack("?", self._redis.get(__class__._KEEPALIVE_KEY))
        self._set_alive(is_alive)

    def _set_alive(self, alive):
        # If the value flipped, log it, then update our state
        if alive != self._alive:
            logger.info(f"Keepalive went {'up' if alive else 'down'}")
        self._alive = alive

    def _before_close(self):
        self._set_alive(False)
