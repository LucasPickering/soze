import json
from datetime import datetime

import lcd
from color import Color


class LcdMode(json.JSONEncoder):

    def __init__(self, config, user_settings, mode_name):
        self.config = config
        self.user_settings = user_settings

    def get_text(self):
        return None


class LcdModeOff(LcdMode):

    BLACK = Color(0, 0, 0)

    def get_color(self):
        return self.BLACK

    def get_text(self):
        return ''


class LcdModeClock(LcdMode):

    LONG_DAY_FORMAT = '%A, %B %d'
    SHORT_DAY_FORMAT = '%A, %b %d'
    SECONDS_FORMAT = ' %S'
    TIME_FORMAT = ' %I:%M'

    def get_color(self):
        return self.user_settings.lcd_color

    def get_text(self):

        now = datetime.now()
        day_str = now.strftime(self.LONG_DAY_FORMAT)
        seconds_str = now.strftime(self.SECONDS_FORMAT)

        # If the line is too long, use a shorter version
        if len(day_str) + len(seconds_str) > self.config.lcd_width:
            day_str = now.strftime(self.SHORT_DAY_FORMAT)

        # Pad the day string with spaces to make it the right length
        day_str = day_str.ljust(self.config.lcd_width - len(seconds_str))
        first_line = day_str + seconds_str

        time_str = now.strftime(self.TIME_FORMAT)
        time_lines = lcd.make_big_text(time_str)

        return '\n'.join([first_line] + time_lines)


_names = {
    'off': LcdModeOff,
    'clock': LcdModeClock
}


def get_by_name(name, config, user_settings):
    try:
        return _names[name](config, user_settings, name)
    except KeyError:
        raise ValueError("Invalid name: {}. Valid names are: {}".format(name, _names.keys()))
