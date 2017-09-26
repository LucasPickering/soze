from ccs.core.decorators import registered_singleton
from .mode import LedMode, MODES


@registered_singleton(MODES, 'static')
class StaticMode(LedMode):

    def _get_color(self, settings):
        return settings.get('led.static.color')
