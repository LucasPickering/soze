from ccs.core.color import BLACK
from ccs.core.decorators import registered_singleton
from .mode import LedMode, MODES


@registered_singleton(MODES, 'off')
class OffMode(LedMode):

    def _get_color(self, settings):
        return BLACK
