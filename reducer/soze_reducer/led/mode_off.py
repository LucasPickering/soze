from soze_reducer.core.color import BLACK
from soze_reducer.core.mode import register
from .mode import LedMode


@register("off", LedMode.MODES)
class OffMode(LedMode):
    def __init__(self):
        super().__init__("off")

    def get_color(self, settings):
        return BLACK
