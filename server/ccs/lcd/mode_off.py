from ccs.core.color import BLACK
from .mode import LcdMode


class OffMode(LcdMode):

    def _get_color(self, lcd, settings):
        return BLACK

    def _get_text(self, lcd, settings):
        return ''
