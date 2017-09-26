from datetime import datetime

from ccs.core.decorators import registered_singleton
from . import helper
from .mode import LcdMode, MODES


@registered_singleton(MODES, 'clock')
class ClockMode(LcdMode):

    _LONG_DAY_FORMAT = '{d:%A}, {d:%B} {d.day}'
    _SHORT_DAY_FORMAT = '{d:%A}, {d:%b} {d.day}'
    _SECONDS_FORMAT = ' {d:%S}'
    _TIME_FORMAT = '{d:%l}:{d:%M}'

    def _get_color(self, lcd, settings):
        return settings.get('lcd.color')

    def _get_text(self, lcd, settings):
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
        time_lines = helper.make_big_text(time_str)  # Rest of the fucking lines
        lines += [' {}'.format(line) for line in time_lines]  # Pad each line with a space

        return '\n'.join(lines)
