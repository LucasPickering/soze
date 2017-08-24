from datetime import datetime

from . import lcd
from ccs.core.color import BLACK

_LONG_DAY_FORMAT = '%A, %B %d'
_SHORT_DAY_FORMAT = '%A, %b %d'
_SECONDS_FORMAT = ' %S'
_TIME_FORMAT = ' %I:%M'


def _get_lcd_color():
    from ccs.core import user_settings  # Workaround!!
    return user_settings.lcd_color


def _get_clock_text():
    from ccs.core import config  # Workaround!!

    now = datetime.now()
    day_str = now.strftime(_LONG_DAY_FORMAT)
    seconds_str = now.strftime(_SECONDS_FORMAT)

    # If the line is too long, use a shorter version
    if len(day_str) + len(seconds_str) > config.lcd_width:
        day_str = now.strftime(_SHORT_DAY_FORMAT)

    # Pad the day string with spaces to make it the right length
    day_str = day_str.ljust(config.lcd_width - len(seconds_str))
    first_line = day_str + seconds_str

    time_str = now.strftime(_TIME_FORMAT)
    time_lines = lcd.make_big_text(time_str)

    return '\n'.join([first_line] + time_lines)


_MODE_DICT = {
    'off': (lambda: BLACK, lambda: ''),
    'clock': (_get_lcd_color, _get_clock_text),
}


def get_color_and_text(mode):
    """
    @brief      Gets the current color and text for the LCD.

    @param      mode  The current LCD mode, as a string

    @return     The current LCD color and text, in a tuple, based on mode and other settings.

    @raises     ValueError if the given LCD mode is unknown
    """
    try:
        get_color, get_text = _MODE_DICT[mode]  # Get the functions used for this mode
    except KeyError:
        valid_modes = _MODE_DICT.keys()
        raise ValueError(f"Invalid mode '{mode}'. Valid modes are {valid_modes}")
    return (get_color(), get_text())
