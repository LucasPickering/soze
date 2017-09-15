#!/usr/bin/env python3

import abc
import curses
import socket
import struct
import time
from threading import Thread

from ccs.core.color import Color, BLACK
from ccs.led.helper import LED_PWM_SOCKET, LED_RED_PIN, LED_GREEN_PIN, LED_BLUE_PIN
from ccs.lcd.helper import *


class Resource(metaclass=abc.ABCMeta):

    def __init__(self, sock_addr):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._addr = sock_addr
        self._thread = Thread(target=self._loop)
        self._run = True

    @abc.abstractmethod
    def _read_data(self):
        pass

    def _loop(self):
        while self._run:
            try:
                self._read_data()
            except socket.error:
                pass

    def start(self):
        self._sock.connect(self._addr)
        self._thread.start()

    def wait(self):
        if self._thread.is_alive():
            self._thread.join()

    def stop(self):
        self._run = False
        self.wait()

        print(f"Closing {self}")
        self._sock.close()

    def __str__(self):
        return self._addr


class ColorPwmSocket(Resource):
    """
    @brief      A mocked version of the LED handler.
    """

    def __init__(self, pin, x=0, y=0):
        super().__init__(LED_PWM_SOCKET.format(pin=pin))
        self.val = 0

    def _read_data(self):
        data = self._sock.recv(4)  # 4 bytes per float
        dc = struct.unpack('f', data)[0]
        self.val = int(dc / 100.0 * 255.0)


_lcd_commands = {}


def command(code, num_args=0):
    def inner(func):
        def wrapper(*args):
            func(*args)
        _lcd_commands[code] = (num_args, func)
        return wrapper
    return inner


class LcdSocket(Resource):
    """
    @brief      Where the magic happens for mocking the LCD.
    """

    def __init__(self):
        super().__init__(LCD_MOCK_SOCKET)

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
        self._socket_buffer = bytearray()

        self._width = DEFAULT_WIDTH
        self._height = DEFAULT_HEIGHT
        self._text = [''] * self._height
        self._cursor_x = 0
        self._cursor_y = 0
        self._color = BLACK

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def text(self):
        return '\n'.join(self._text)

    @property
    def cursor_pos(self):
        return (self._cursor_x, self._cursor_y)

    @property
    def color(self):
        return self._color

    @command(CMD_CLEAR)
    def _clear(self):
        self.text = [''] * self._height

    @command(CMD_SIZE, 2)
    def _set_size(self, width, height):
        self._width = width
        self._height = height

    @command(CMD_COLOR, 3)
    def _set_color(self, red, green, blue):
        self._color = Color(red, green, blue)

    @command(CMD_CURSOR_POS, 2)
    def _set_cursor_pos(self, x, y):
        if self._width is None or self._height is None:
            raise ValueError("Width and height must be set before setting cursor pos")
        better_x = x - 1  # Fuck 1-indexing
        better_y = y - 1  # Once again, fuck 1-indexing
        wrapped_x = better_x % self._width  # Wrap on x
        wrapped_y = (int(better_x / self._width) + better_y) % self._height  # Wrap on x and y
        self._cursor_x = wrapped_x
        self._cursor_y = wrapped_y

    @command(CMD_CURSOR_HOME)
    def _cursor_home(self):
        self._set_cursor_pos(1, 1)

    @command(CMD_CURSOR_FWD)
    def _cursor_fwd(self, n=1):
        self._set_cursor_pos(self._cursor_x + n, self._cursor_y)

    @command(CMD_CURSOR_BACK)
    def _cursor_back(self, n=1):
        self._set_cursor_pos(self._cursor_x - n, self._cursor_y)

    @command(CMD_SAVE_CUSTOM_CHAR, 3)
    def _save_custom_char(self, bank, code, char_bytes):
        # We can't do anything with the custom chars, so don't bother saving them
        # self._custom_chars[bank][code] = char_bytes
        pass

    @command(CMD_LOAD_CHAR_BANK, 1)
    def _load_char_bank(self, bank):
        self._current_char_bank = self._custom_chars[bank]

    def _write_str(self, s):
        x = self._cursor_x - 1
        y = self._cursor_y - 1
        n = len(s)
        line = self._text[y]
        self._text[y] = (line[:x] + s + line[x + n:])[:self._width]  # No text wrapping
        self._cursor_fwd(n)

    def _read_data(self):
        byte = self._sock.recv(1)[0]  # Get the first byte
        if byte == SIG_COMMAND:
            cmd = self._sock.recv(1)[0]  # Get the command byte
            try:
                num_args, cmd_func = _lcd_commands[cmd]  # Figure out how many args we want
            except KeyError:
                raise ValueError(f"Unknown command: 0x{cmd:02x}")

            args = bytearray()
            while len(args) < num_args:
                args += self._sock.recv(1)
            cmd_func(self, *args)  # Call the function with the args
        else:
            # Data is just text, write to the screen
            if self._current_char_bank and byte in self._current_char_bank:
                c = self._current_char_bank[byte]
            else:
                c = chr(byte)
            self._write_str(c)


class CursesDisplay:

    PAUSE = 0.1

    def __init__(self, stdscr, red_pwm, green_pwm, blue_pwm, lcd):
        self._red_pwm = red_pwm
        self._green_pwm = green_pwm
        self._blue_pwm = blue_pwm
        self._lcd = lcd

        self._led_window = curses.newwin(1, 50, 0, 0)
        self._lcd_window = curses.newwin(0, 0, 1, 0)

    def start(self):
        thread = Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        while True:
            led_color = Color(self._red_pwm.val, self._green_pwm.val, self._blue_pwm.val)
            led_str = f"LCD color: ({led_color.red}, {led_color.green}, {led_color.blue})"
            self._led_window.clear()
            self._led_window.addstr(led_str, curses.color_pair(led_color.to_term_color()))
            self._led_window.refresh()

            lcd = self._lcd
            cursor_x, cursor_y = lcd.cursor_pos
            self._lcd_window.clear()
            self._lcd_window.resize(lcd.height + 2, lcd.width + 2)  # +2 for border
            self._lcd_window.border()
            self._lcd_window.addstr(1, 1, lcd.text)
            self._lcd_window.refresh()

            time.sleep(CursesDisplay.PAUSE)


def main(stdscr):
    resources = []

    try:
        curses.curs_set(0)  # Hide the cursor

        # # Add curses colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, curses.COLORS):
            curses.init_pair(i, i, -1)  # Background is always blank

        resources = [
            ColorPwmSocket(LED_RED_PIN),
            ColorPwmSocket(LED_GREEN_PIN),
            ColorPwmSocket(LED_BLUE_PIN),
            LcdSocket(),
        ]

        # Start each resource, then wait for it to stop
        for res in resources:
            res.start()

        display = CursesDisplay(stdscr, *resources)
        display.start()

        for res in resources:
            res.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for res in resources:
            res.stop()


if __name__ == '__main__':
    curses.wrapper(main)
