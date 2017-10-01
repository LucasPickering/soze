#!/usr/bin/env python3

import abc
import argparse
import curses
import logging
import os
import socket
import struct
import time
import traceback
from threading import Thread

from ccs.util import config
from ccs.util.color import Color
from ccs.mock.mock_server import PWM_SOCKET, LCD_SOCKET
from ccs.lcd.helper import *

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'f': {
            'format': '[{asctime} {threadName:<11} {levelname}] {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'f',
            'filename': 'gui.log',
            'mode': 'w',
        },
    },
    'loggers': {
        __name__: {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
})
logger = logging.getLogger(__name__)


class Resource(metaclass=abc.ABCMeta):

    def __init__(self, name, sock_addr):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._addr = sock_addr
        self._thread = Thread(target=self._loop, name='{}-Thread'.format(name), daemon=True)
        self._run = True

    def _read_data(self):
        return self._sock.recv(64)

    @abc.abstractmethod
    def _process_data(self, data):
        pass

    def _loop(self):
        try:
            while self._run:
                data = self._read_data()
                logger.debug(format_bytes(data))
                self._process_data(data)
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            self.close()

    def start(self):
        self._sock.bind(self._addr)
        self._thread.start()

    def close(self):
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            logger.info(f"Closed {self}")
        except Exception:
            pass
        finally:
            if os.path.exists(self._addr):
                os.unlink(self._addr)

    def __str__(self):
        return self._addr


class ColorPwmSocket(Resource):
    """
    @brief      A mocked version of the LED handler.
    """

    def __init__(self, pin, x=0, y=0):
        super().__init__('PWM{}'.format(pin), PWM_SOCKET.format(pin=pin))
        self.val = 0

    def _process_data(self, data):
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
        super().__init__('LCD', LCD_SOCKET)
        self._window = curses.newwin(0, 0, 1, 0)

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

        self._width, self._height = None, None
        self._cursor_x, self._cursor_y = 0, 0

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
        self._window.bkgd(' ', color_pair)
        self._window.noutrefresh()

    @command(CMD_CURSOR_POS, 2)
    def _set_cursor_pos(self, x, y):
        if self._width is None or self._height is None:
            raise ValueError("Width and height must be set before setting cursor pos")
        better_x = x - 1  # Fuck 1-indexing
        better_y = y - 1  # Once again, fuck 1-indexing
        wrapped_x = better_x % self._width  # Wrap on x
        wrapped_y = (int(better_x / self._width) + better_y) % self._height  # Wrap on x and y
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
                num_args, cmd_func = _lcd_commands[cmd]  # Figure out how many args we want
            except KeyError:
                logger.error(f"Unknown command {hex(cmd)} in {format_bytes(data)}")
            args = data[2:]
            if len(args) != num_args:
                logger.error(f"Expected {num_args} args, got {len(args)}: {format_bytes(data)}")

            cmd_func(self, *args)  # Call the function with the args
        else:
            # Data is just text, write to the screen
            s = ''.join(decode_byte(b) for b in data)
            self._write_str(s)


def update_window(red_pwm, green_pwm, blue_pwm, interval):
    window = curses.newwin(1, 30, 0, 0)
    while True:
        r, g, b = red_pwm.val, green_pwm.val, blue_pwm.val
        curses_color = curses.color_pair(Color(r, g, b).to_term_color())

        window.clear()
        window.addstr(f"LED Color: ({r}, {g}, {b})", curses_color)
        window.noutrefresh()

        curses.doupdate()
        time.sleep(interval)


def main(stdscr):
    curses.curs_set(0)  # Hide the cursor

    # Add curses colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(1, curses.COLORS):
        curses.init_pair(i, i, -1)  # Background is always blank

    cfg = config['led']
    resources = [
        ColorPwmSocket(cfg['red_pin']),
        ColorPwmSocket(cfg['green_pin']),
        ColorPwmSocket(cfg['blue_pin']),
        LcdSocket(),
    ]

    try:
        # Start each resource, then wait for it to stop
        for res in resources:
            res.start()

        curses_thread = Thread(target=update_window, name='Curses-Thread',
                               args=[*resources[:3], 0.05], daemon=True)
        curses_thread.start()

        # Wait for Ctrl-c
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.error(traceback.format_exc())
    finally:
        for res in resources:
            res.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('working_dir', nargs='?', default='.',
                        help="Directory to store settings, config, etc.")
    args = parser.parse_args()
    config.init(args.working_dir)
    curses.wrapper(main)
