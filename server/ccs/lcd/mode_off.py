from ccs.core.color import BLACK
from ccs.core.decorators import registered_singleton
from .mode import LcdMode, MODES


@registered_singleton(MODES, 'off')
class OffMode(LcdMode):

    def _get_color(self, lcd, settings):
        return BLACK

    def _get_text(self, lcd, settings):
        return ''
