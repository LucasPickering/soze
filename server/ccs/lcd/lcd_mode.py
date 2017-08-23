import json
from datetime import datetime

from . import lcd
from ccs.core.color import BLACK


class LcdMode(json.JSONEncoder):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def get_text(self):
        return None


class LcdModeOff(LcdMode):

    NAME = 'off'

    def get_color(self):
        return BLACK

    def get_text(self):
        return ''


class LcdModeClock(LcdMode):

    NAME = 'clock'

    LONG_DAY_FORMAT = '%A, %B %d'
    SHORT_DAY_FORMAT = '%A, %b %d'
    SECONDS_FORMAT = ' %S'
    TIME_FORMAT = ' %I:%M'

    def get_color(self):
        from ccs.core import user_settings  # Workaround!!
        return user_settings.lcd_color

    def get_text(self):
        from ccs.core import config  # Workaround!!

        now = datetime.now()
        day_str = now.strftime(self.LONG_DAY_FORMAT)
        seconds_str = now.strftime(self.SECONDS_FORMAT)

        # If the line is too long, use a shorter version
        if len(day_str) + len(seconds_str) > config.lcd_width:
            day_str = now.strftime(self.SHORT_DAY_FORMAT)

        # Pad the day string with spaces to make it the right length
        day_str = day_str.ljust(config.lcd_width - len(seconds_str))
        first_line = day_str + seconds_str

        time_str = now.strftime(self.TIME_FORMAT)
        time_lines = lcd.make_big_text(time_str)

        return '\n'.join([first_line] + time_lines)


_classes = [LcdModeOff, LcdModeClock]
_names = {cls.NAME: cls for cls in _classes}


def get_by_name(name):
    try:
        return _names[name](name)
    except KeyError:
        valid_names = list(_names.keys())
        raise ValueError(f"Invalid name: {name}. Valid names are: {valid_names}")
