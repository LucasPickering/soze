from .mode import LedMode


class StaticMode(LedMode):

    def _get_color(self, settings):
        return settings.get('led.static.color')
