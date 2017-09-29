from ccs.util.color import BLACK
from .mode import LedMode


class OffMode(LedMode):

    def _get_color(self, settings):
        return BLACK
