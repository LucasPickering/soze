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
        # struct.unpack returns a 1-tuple, we want to get the only field
        is_alive, = struct.unpack(
            "?", self._redis.get(__class__._KEEPALIVE_KEY)
        )

        # If the value flipped, log it, then update our state
        if is_alive != self._alive:
            logger.info(f"Keepalive went {'up' if is_alive else 'down'}")
        self._alive = is_alive
