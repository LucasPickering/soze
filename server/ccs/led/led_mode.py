import abc

from ccs.core.decorators import registered_singleton
from ccs.core.named import Named
from ccs.core.color import Color, RED, BLACK

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

    def _get_color(self, settings):
        return RED
