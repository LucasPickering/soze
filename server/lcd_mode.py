from color import Color
from datetime import datetime


class LcdMode:

    def __init__(self, config, user_settings):
        self.config = config
        self.user_settings = user_settings

    def should_update_color(self):
        return self.color_updated

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
    HM_FORMAT = '%I:%M'
    FIRST_LINE_FORMAT = '{} {}'

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

        return first_line


_names = {
    'off': LcdModeOff,
    'clock': LcdModeClock
}


def get_by_name(name, config, user_settings):
    try:
        return _names[name](config, user_settings)
    except KeyError:
        raise ValueError("Invalid name: {}. Valid names are: {}".format(name, _names.keys()))
