import abc

from ccs.core.named import Named
from ccs.core.color import BLACK


class LedMode(Named):

    @abc.abstractmethod
    def get_color(self, settings):
        pass


class OffMode(LedMode):

    def __init__(self):
        super().__init__('off')

    def get_color(self, settings):
        return BLACK


class StaticMode(LedMode):

    def __init__(self):
        super().__init__('static')

    def get_color(self, settings):
        return settings.get('led.static.color')


_MODES = [OffMode(), StaticMode()]
_MODE_DICT = {mode.name: mode for mode in _MODES}
MODE_NAMES = set(_MODE_DICT.keys())


def get_color(settings):
    """
    @brief      Gets the current color for the LEDs.

    @param      settings  The current settings

    @return     The current LED color, based on mode and other relevant settings.

    @raises     ValueError if the given LED mode is unknown
    """
    try:
        mode = _MODE_DICT[settings.get('led.mode')]  # Get the relevant mode object
    except KeyError:
        raise ValueError(f"Invalid mode '{mode}'. Valid modes are {MODE_NAMES}")
    return mode.get_color(settings)
