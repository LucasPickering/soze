import time

from soze_reducer.core.color import BLACK
from soze_reducer.core.mode import register
from .mode import LedMode


@register("fade", LedMode.MODES)
class FadeMode(LedMode):
    def __init__(self):
        super().__init__("fade")
        self._color_index = 0
        self._fade_start_time = 0

    def get_color(self, settings):
        fade_colors = settings.get("led.fade.colors")
        fade_time = settings.get("led.fade.fade_time")

        if len(fade_colors) == 0:
            return BLACK

        def get_fade_color(index):
            return fade_colors[index % len(fade_colors)]

        now = time.time()
        if now - self._fade_start_time >= fade_time:
            # Reached the next color
            self._color_index += 1
            self._color_index %= len(fade_colors)
            self._fade_start_time = now

        # Interpolate between the two boundary colors based on time
        last_color = get_fade_color(self._color_index)
        next_color = get_fade_color(self._color_index + 1)
        bias = (now - self._fade_start_time) / fade_time
        current_color = last_color * (1 - bias) + next_color * bias
        return current_color
