from soze_reducer.core.color import BLACK, Color
from soze_reducer.core.mode import register
from .mode import LedMode


@register("static", LedMode.MODES)
class StaticMode(LedMode):
    def __init__(self):
        super().__init__("static")

    def get_color(self, settings):
        try:
            return Color.from_hexcode(settings["static"]["color"])
        except KeyError:
            return BLACK
