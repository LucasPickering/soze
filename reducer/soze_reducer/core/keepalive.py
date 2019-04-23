import struct
from enum import Enum

from soze_reducer import logger
from .resource import RedisSubscriber


class Status(Enum):
    NORMAL = "normal"
    SLEEP = "sleep"


class Keepalive(RedisSubscriber):

    _KEEPALIVE_KEY = "reducer:keepalive"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, sub_channel="r2d:keepalive", **kwargs)
        self._alive = False
        # List of functions to call after a status change
        self._listeners = []

    @property
    def status(self):
        status = Status.NORMAL if self._alive else Status.SLEEP
        return status.value

    def register_listener(self, listener):
        self._listeners.append(listener)

    def _on_pub(self, msg):
        # struct.unpack returns a 1-tuple, we want to get the only field
        is_alive, = struct.unpack(
            "?", self._redis.get(__class__._KEEPALIVE_KEY)
        )

        # If the value changed, update our state, log it, then call listeners
        if is_alive != self._alive:
            self._alive = is_alive
            logger.info(f"Keepalive went {'up' if is_alive else 'down'}")
            for listener in self._listeners:
                listener(self.status)
