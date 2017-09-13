#!/usr/bin/env python3

import abc
import curses
import os
import socket
import struct
import threading

from ccs.core.color import Color, BLACK
from ccs.led.helper import LED_PWM_SOCKET, LED_RED_PIN, LED_GREEN_PIN, LED_BLUE_PIN
from ccs.lcd.helper import *


class Resource(metaclass=abc.ABCMeta):

    def __init__(self, sock_addr, width, height, x, y):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        self._addr = sock_addr
        self._window = curses.newwin(height, width, y, x)
        self._thread = threading.Thread(target=self._loop)
        self._run = True

    @abc.abstractmethod
    def _process_data(self, data):
        pass

    def _loop(self):
        while self._run:
            try:
                data = self._sock.recv(1024)
                self._process_data(data)
            except socket.error:
                pass

    def _close(self):
        print(f"Closing {self}")
        self._sock.close()
        os.remove(self._addr)

    def start(self):
        self._sock.bind(self._addr)
        self._thread.start()

    def wait(self):
        if self._thread.is_alive():
            self._thread.join()

    def stop(self):
        self._run = False
        self.wait()
        self._close()

    def __str__(self):
        return self._addr


class CursesLed(Resource):
    """
    @brief      A mocked version of the LED handler.
    """

    WIDTH = 50
    HEIGHT = 1

    def __init__(self, pin, x=0, y=0):
        super().__init__(LED_PWM_SOCKET.format(pin=pin), CursesLed.WIDTH, CursesLed.HEIGHT, x, y)

    def _process_data(self, data):
        def dc_to_color(dc):
            return dc / 100.0
        dc = struct.unpack('f', data)[0]
        color_val = int(dc / 100.0 * 255.0)
        self._window.addstr(0, 0, f"{color_val:<3}")
        self._window.refresh()


class CursesLcd(Resource):
    """
    @brief      Where the magic happens for mocking the LCD.
    """

    _CMD_FUNCS = {
        CMD_CLEAR: lambda self, args: self._clear(),
        CMD_BACKLIGHT_ON: lambda self, args: None,
        CMD_BACKLIGHT_OFF: lambda self, args: None,
        CMD_SIZE: lambda self, args: self._set_size(*args),
        CMD_SPLASH_TEXT: lambda self, args: None,
        CMD_BRIGHTNESS: lambda self, args: None,
        CMD_CONTRAST: lambda self, args: None,
        CMD_COLOR: lambda self, args: self._set_color(*args),
        CMD_AUTOSCROLL_ON: lambda self, args: None,  # Not supporting (always off)
        CMD_AUTOSCROLL_OFF: lambda self, args: None,
        CMD_UNDERLINE_CURSOR_ON: lambda self, args: None,
        CMD_UNDERLINE_CURSOR_OFF: lambda self, args: None,
        CMD_BLOCK_CURSOR_ON: lambda self, args: None,
        CMD_BLOCK_CURSOR_OFF: lambda self, args: None,
        CMD_CURSOR_HOME: lambda self, args: self._set_cursor_pos(1, 1),
        CMD_CURSOR_POS: lambda self, args: self._set_cursor_pos(*args),
        CMD_CURSOR_FWD: lambda self, args: self._cursor_fwd(),
        CMD_CURSOR_BACK: lambda self, args: self._cursor_back(),
        CMD_CREATE_CHAR: lambda self, args: None,  # This thing is useless
        CMD_SAVE_CUSTOM_CHAR: lambda self, args: self._save_custom_char(args[0], args[1], args[2:]),
        CMD_LOAD_CHAR_BANK: lambda self, args: self._load_char_bank(args[0]),
    }

    def __init__(self, x=0, y=0):
        super().__init__(LCD_MOCK_SOCKET, 0, 0, x, y)

        # Unfortunately this has to be hardcoded
        self._custom_chars = {
            0: {
                0x00: '▗',  # Half-bottom right
                0x01: '▖',  # Half-bottom left
                0x02: '▄',  # Half-bottom
                0x03: '▜',  # Full-bottom right
                0x04: '▛',  # Full-bottom left
                0xff: '█',  # Full
            }
        }
        self._current_char_bank = None
        self._color = BLACK

        self._border()  # Draw a border for the window

    def _border(self):
        self._window.border()
        self._window.refresh()

    def _clear(self):
        self._window.clear()
        self._border()

    def _set_size(self, width, height):
        self._width = width
        self._height = height
        self._window.clear()
        self._window.refresh()
        self._window.resize(height + 3, width + 2)
        self._border()

    def _set_color(self, red, green, blue):
        self._color = Color(red, green, blue)
        s = str(self._color).ljust(self._width)
        term_color = self._color.to_term_color()
        self._window.addstr(self._height + 1, 1, s, curses.color_pair(term_color))
        self._window.refresh()

    def _set_cursor_pos(self, x, y):
        if self._width is None or self._height is None:
            raise ValueError("Width and height must be set before setting cursor pos")
        better_x = x - 1  # Fuck 1-indexing
        better_y = y - 1  # Once again, fuck 1-indexing
        wrapped_x = better_x % self._width  # Wrap on x
        wrapped_y = (int(better_x / self._width) + better_y) % self._height  # Wrap on x and y
        self._cursor_x = wrapped_x + 1
        self._cursor_y = wrapped_y + 1

    def _cursor_fwd(self):
        self._set_cursor_pos(self._cursor_x + 1, self._cursor_y)

    def _cursor_back(self):
        self._set_cursor_pos(self._cursor_x - 1, self._cursor_y)

    def _save_custom_char(self, bank, code, char_bytes):
        # We can't do anything with the custom chars, so don't bother saving them
        # self._custom_chars[bank][code] = char_bytes
        pass

    def _load_char_bank(self, bank):
        self._current_char_bank = self._custom_chars[bank]

    def _receive_data(self):
        return self._ser.read(128)

    def _process_data(self, data):
        if data[0] == SIG_COMMAND:
            cmd = data[1]
            args = data[2:]
            try:
                # logger.debug(hex(cmd))
                cmd_func = CursesLcd._CMD_FUNCS[cmd]  # Get the function for this command
            except KeyError:
                raise ValueError(f"Unknown command: 0x{cmd:02x}")
            cmd_func(self, args)  # Call the function with the args
        else:
            # Data is just text, write to the screen
            s = data.decode()
            if self._current_char_bank:
                for code, char in self._current_char_bank.items():
                    s = s.replace(chr(code), char)
            self._window.clear()
            self._window.addstr(self._cursor_y, self._cursor_x, s)
            self._window.refresh()


if __name__ == '__main__':
    stdscr = curses.initscr()

    curses.curs_set(0)  # Hide the cursor

    # Add curses colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(1, curses.COLORS):
        curses.init_pair(i, i, -1)  # Background is always blank

    resources = []
    try:
        resources = [
            CursesLed(LED_RED_PIN, y=0),
            CursesLed(LED_GREEN_PIN, y=1),
            CursesLed(LED_BLUE_PIN, y=2),
            CursesLcd(y=3),
        ]

        # Start each resource, then wait for it to stop
        for res in resources:
            res.start()
        for res in resources:
            res.wait()
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()

        for res in resources:
            res.stop()
