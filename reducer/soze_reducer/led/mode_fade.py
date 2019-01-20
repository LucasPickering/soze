import time

from soze_reducer.core.color import BLACK, Color
from soze_reducer.core.mode import register
from .mode import LedMode


@register("fade", LedMode.MODES)
class FadeMode(LedMode):

    _FADE_COLORS_KEY = "fade:colors"
    _FADE_TIME_KEY = "fade:fade_time"

    def __init__(self):
        super().__init__("fade")
        self._color_index = 0
        self._fade_start_time = 0

    def get_color(self, settings):
        try:
            fade_settings = settings["fade"]
            fade_colors = [
                Color.from_hexcode(color_bytes)
                for color_bytes in fade_settings["colors"]
            ]
            fade_time = float(fade_settings["fade_time"])
        except KeyError:
            # One or more key is missing from Redis
            return BLACK

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
