import abc

from datetime import datetime

from .lcd import Lcd
from ccs.core.named import Named
from ccs.core.color import BLACK


class LcdMode(Named):

    @abc.abstractmethod
    def get_color(self, lcd, settings):
        pass

    @abc.abstractmethod
    def get_text(self, lcd, settings):
        pass


class OffMode(LcdMode):

    def __init__(self):
        super().__init__('off')

    def get_color(self, lcd, settings):
        return BLACK

    def get_text(self, lcd, settings):
        return ''


class ClockMode(LcdMode):

    _LONG_DAY_FORMAT = '{d:%A}, {d:%B} {d.day}'
    _SHORT_DAY_FORMAT = '{d:%A}, {d:%b} {d.day}'
    _SECONDS_FORMAT = ' {d.second:02}'
    _TIME_FORMAT = ' {d:%I}:{d.minute:02}'

    def __init__(self):
        super().__init__('clock')

    def get_color(self, lcd, settings):
        return settings.get('lcd.color')

    def get_text(self, lcd, settings):
        lines = []  # This will we populated as we go along

        now = datetime.now()
        day_str = ClockMode._LONG_DAY_FORMAT.format(d=now)
        seconds_str = ClockMode._SECONDS_FORMAT.format(d=now)

        # If the line is too long, use a shorter version
        if len(day_str) + len(seconds_str) > lcd.width:
            day_str = ClockMode._SHORT_DAY_FORMAT.format(d=now)

        # Pad the day string with spaces to make it the right length
        day_str = day_str.ljust(lcd.width - len(seconds_str))
        lines.append(day_str + seconds_str)  # First line

        time_str = ClockMode._TIME_FORMAT.format(d=now)
        lines += Lcd.make_big_text(time_str)  # Rest of the fucking lines

        return '\n'.join(lines)


_MODES = [OffMode(), ClockMode()]
_MODE_DICT = {mode.name: mode for mode in _MODES}
MODE_NAMES = set(_MODE_DICT.keys())


def get_color_and_text(lcd, settings):
    """
    @brief      Gets the current color and text for the LCD.

    @param      settings  The current settings

    @return     The current LCD color and text, in a tuple, based on mode and other settings.

    @raises     ValueError if the given LCD mode is unknown
    """
    try:
        mode = _MODE_DICT[settings.get('lcd.mode')]  # Get the relevant mode object
    except KeyError:
        raise ValueError(f"Invalid mode '{mode}'. Valid modes are {MODE_NAMES}")
    return (mode.get_color(lcd, settings), mode.get_text(lcd, settings))
