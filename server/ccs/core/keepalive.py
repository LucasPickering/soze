import struct

from ccs import logger
from .socket_resource import SocketResource


class Keepalive(SocketResource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, pause=1.0, **kwargs)
        self._alive = False

    @property
    def name(self):
        return 'Keepalive'

    @property
    def is_alive(self):
        return self._alive

    def _set_alive(self, alive):
        # If the value flipped, log it, then update our state
        if alive != self._alive:
            logger.info(f"Keepalive went {'up' if alive else 'down'}")
        self._alive = alive

    def _update(self, *args):
        self._send(b'\x00')
        val = self._read()
        alive = bool(val and struct.unpack('?', val)[0])  # Unpack returns a tuple of (bool,)
        self._set_alive(alive)

    def _close(self):
        super()._close()
        self._set_alive(False)
