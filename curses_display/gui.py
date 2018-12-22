#!/usr/bin/env python3

import curses
import logging
import time
from threading import Thread

from soze_core.component import SozeComponent
from soze_core.resource import ReadResource, WriteResource, format_bytes

from soze_server.core.color import Color, BLACK
from soze_server.lcd.helper import *

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "f": {
                "format": "{asctime} [{threadName} {levelname}] {message}",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{",
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "formatter": "f",
                "filename": "gui.log",
                "mode": "w",
            }
        },
        "loggers": {__name__: {"handlers": ["file"], "level": "DEBUG"}},
    }
)
logger = logging.getLogger(__name__)

CFG_FILE = "sozed.json"
DEFAULT_CFG = {
    "led": {
        "socket_addr": "/tmp/soze_led.sock",
        "hat_addr": 0x60,
        "pins": [3, 1, 2],  # RGB
    },
    "lcd": {"socket_addr": "/tmp/soze_lcd.sock", "serial_port": "/dev/ttyAMA0"},
    "keepalive": {"socket_addr": "/tmp/soze_keepalive.sock", "pin": 4},
}


class CursesResource(ReadResource):
    def __init__(self, dimensions, *args, **kwargs):
        super().__init__(*args, **kwargs)

        x, y, width, height = dimensions
        self._window = curses.newwin(height, width, y, x)


class Led(CursesResource):
    """
    @brief      A mocked version of the LED handler.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(dimensions=(0, 0, 50, 1), *args, **kwargs)
        self._set_color(BLACK)

    @property
    def name(self):
        return "LED"

    def _set_color(self, color):
        curses_color = curses.color_pair(color.to_term_color())
        self._window.clear()
        self._window.addstr(f"LED Color: {color}", curses_color)
        self._window.noutrefresh()

    def _process_data(self, data):
        self._set_color(Color.from_bytes(data))


_lcd_commands = {}


class Lcd(CursesResource):
    """
    @brief      Where the magic happens for mocking the LCD.
    """

    def command(code, num_args=0):
        def inner(func):
            def wrapper(*args):
                func(*args)

            _lcd_commands[code] = (num_args, func)
            return wrapper

        return inner

    def __init__(self, *args, **kwargs):
        super().__init__(dimensions=(0, 1, 0, 0), *args, **kwargs)

        # Unfortunately this has to be hardcoded
        self._custom_chars = {
            0: {
                0x00: "▗",  # Half-bottom right
                0x01: "▖",  # Half-bottom left
                0x02: "▄",  # Half-bottom
                0x03: "▜",  # Full-bottom right
                0x04: "▛",  # Full-bottom left
                0xFF: "█",  # Full
            }
        }
        self._current_char_bank = None

        self._width, self._height = None, None
        self._cursor_x, self._cursor_y = 0, 0

    @property
    def name(self):
        return "LCD"

    @command(CMD_CLEAR)
    def _clear(self):
        self._window.clear()
        self._window.border()
        self._window.noutrefresh()

    @command(CMD_BACKLIGHT_ON, 1)
    def _backlight_on(self, timeout):  # timeout is unused in Adafruit's driver
        pass  # TODO

    @command(CMD_BACKLIGHT_OFF)
    def _backlight_off(self):
        pass  # TODO

    @command(CMD_SIZE, 2)
    def _set_size(self, width, height):
        self._width, self._height = width, height
        self._window.resize(height + 2, width + 2)  # padding for border
        self._window.border()
        self._window.noutrefresh()

    @command(CMD_COLOR, 3)
    def _set_color(self, red, green, blue):
        color = Color(red, green, blue)
        color_pair = curses.color_pair(color.to_term_color())
        self._window.bkgd(" ", color_pair)
        self._window.noutrefresh()

    @command(CMD_CURSOR_POS, 2)
    def _set_cursor_pos(self, x, y):
        if self._width is None or self._height is None:
            raise ValueError(
                "Width and height must be set before setting cursor pos"
            )
        better_x = x - 1  # Fuck 1-indexing
        better_y = y - 1  # Once again, fuck 1-indexing
        wrapped_x = better_x % self._width  # Wrap on x
        wrapped_y = (
            int(better_x / self._width) + better_y
        ) % self._height  # Wrap on x and y
        self._cursor_x = wrapped_x + 1
        self._cursor_y = wrapped_y + 1

    @command(CMD_CURSOR_HOME)
    def _cursor_home(self):
        self._set_cursor_pos(1, 1)

    @command(CMD_CURSOR_FWD)
    def _cursor_fwd(self, n=1):
        self._set_cursor_pos(self._cursor_x + n, self._cursor_y)

    @command(CMD_CURSOR_BACK)
    def _cursor_back(self, n=1):
        self._set_cursor_pos(self._cursor_x - n, self._cursor_y)

    @command(CMD_SAVE_CUSTOM_CHAR, 10)  # bank + code + 8 char bytes
    def _save_custom_char(self, bank, code, *char_bytes):
        # We can't do anything with the custom chars, so don't bother saving them
        # self._custom_chars[bank][code] = char_bytes
        pass

    @command(CMD_LOAD_CHAR_BANK, 1)
    def _load_char_bank(self, bank):
        self._current_char_bank = self._custom_chars[bank]

    @command(CMD_AUTOSCROLL_ON)
    def _autoscroll_on(self):
        pass  # TODO

    @command(CMD_AUTOSCROLL_OFF)
    def _autoscroll_off(self):
        pass  # TODO

    def _write_str(self, s):
        self._window.addstr(self._cursor_y, self._cursor_x, s)
        self._window.noutrefresh()
        self._cursor_fwd(len(s))

    def _process_data(self, data):
        def decode_byte(b):
            try:
                return self._current_char_bank[b]
            except KeyError:
                return chr(b)

        if data[0] == SIG_COMMAND:
            if len(data) < 2:
                logger.error(f"Missing command byte: {format_bytes(data)}")
            cmd = data[1]  # Get the command byte

            try:
                num_args, cmd_func = _lcd_commands[
                    cmd
                ]  # Figure out how many args we want
            except KeyError:
                logger.error(
                    f"Unknown command {hex(cmd)} in {format_bytes(data)}"
                )
            args = data[2:]
            if len(args) == num_args:
                cmd_func(self, *args)  # Call the function with the args
            else:
                logger.error(
                    f"Expected {num_args} args, got {len(args)}: {format_bytes(data)}"
                )
        else:
            # Data is just text, write to the screen
            s = "".join(decode_byte(b) for b in data)
            self._write_str(s)


class Keepalive(WriteResource):
    @property
    def name(self):
        return "Keepalive"

    def _update(self):
        self._write(b"\x01")


class SozeDisplay(SozeComponent):
    def __init__(self, **kwargs):
        super().__init__(cfg_file=CFG_FILE, default_cfg=DEFAULT_CFG, **kwargs)

        curses.curs_set(0)  # Hide the cursor

        # Add curses colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, curses.COLORS):
            curses.init_pair(i, i, -1)  # Background is always blank

    def _init_resources(self, cfg):
        return [
            Led(**cfg["led"]),
            Lcd(**cfg["lcd"]),
            Keepalive(**cfg["keepalive"]),
        ]

    def _get_extra_threads(self, cfg):
        return [
            Thread(
                target=self._update_window, name="Curses-Thread", daemon=True
            )
        ]

    def _update_window(self):
        while True:
            curses.doupdate()
            time.sleep(0.05)


def main(stdscr):
    c = SozeDisplay.from_cmd_args()
    c.run()


if __name__ == "__main__":
    curses.wrapper(main)
