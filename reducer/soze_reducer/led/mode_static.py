from soze_reducer.core.mode import register
from .mode import LedMode


@register("static", LedMode.MODES)
class StaticMode(LedMode):

    _STATIC_COLOR_KEY = "static:color"

    def __init__(self):
        super().__init__("static")

    def get_color(self, settings):
        return settings[__class__._STATIC_COLOR_KEY]
