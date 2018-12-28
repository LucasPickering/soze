from soze_reducer.core.color import BLACK
from soze_reducer.core.mode import register
from .mode import LcdMode


@register("off", LcdMode.MODES)
class OffMode(LcdMode):
    def __init__(self):
        super().__init__("off")

    def get_color(self, settings):
        return BLACK

    def get_text(self, settings):
        return ""
