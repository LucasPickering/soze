from soze_core import logger
from soze_core.resource import ReadResource


class Keepalive(ReadResource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def _process_data(self, data):
        self._set_alive(bool(data[-1]))  # Only the last byte matters

    def _before_close(self):
        self._set_alive(False)
