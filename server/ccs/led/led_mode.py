import abc
import time

from ccs.core.decorators import registered_singleton
from ccs.core.named import Named
from ccs.core.color import BLACK

_modes = {}


class LedMode(Named):

    @abc.abstractmethod
    def _get_color(self, settings):
        pass

    @staticmethod
    def get_mode_names():
        return set(_modes.keys())

    @staticmethod
    def get_color(settings):
        """
        @brief      Gets the current color for the LEDs.

        @param      settings  The current settings

        @return     The current LED color, based on mode and other relevant settings.

        @raises     ValueError if the given LED mode is unknown
        """
        mode = _modes[settings.get('led.mode')]  # Get the relevant mode object
        return mode._get_color(settings)


@registered_singleton(_modes, 'off')
class OffMode(LedMode):

    def _get_color(self, settings):
        return BLACK


@registered_singleton(_modes, 'static')
class StaticMode(LedMode):

    def _get_color(self, settings):
        return settings.get('led.static.color')


@registered_singleton(_modes, 'fade')
class FadeMode(LedMode):

    def __init__(self, name):
        super().__init__(name)
        self._color_index = 0
        self._fade_start_time = 0

    def _get_color(self, settings):
        fade_colors = settings.get('led.fade.colors')
        fade_time = settings.get('led.fade.fade_time')

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
