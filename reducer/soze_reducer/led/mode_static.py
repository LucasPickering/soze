from soze_reducer.core.mode import register
from .mode import LedMode


@register("static", LedMode.MODES)
class StaticMode(LedMode):
    def __init__(self):
        super().__init__("static")

    def get_color(self, settings):
        return settings.get("led.static.color")
