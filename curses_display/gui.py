#!/usr/bin/env python3

import abc
import argparse
import curses
import logging
import os
import socket
import time
import traceback
from threading import Thread

from ccs.core.color import Color, BLACK
from ccs.lcd.helper import *


RETRY_PAUSE = 3  # Time to wait after a failed socket connect before trying again


def format_bytes(data):
    return ' '.join('{:02x}'.format(b) for b in data)


logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'f': {
            'format': '{asctime} [{threadName:<11} {levelname}] {message}',
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
    def __init__(self, name, sock_addr, dims):
        self._sock = None
        self._conn = None
        self._addr = sock_addr
        self._thread = Thread(target=self._loop, name='{}-Thread'.format(name), daemon=True)

        if dims:
            x, y, width, height = dims
            self._window = curses.newwin(height, width, y, x)

        self._run = True

    @property
    def is_open(self):
        return bool(self._sock and self._conn)

    def _open(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(self._addr)
        self._sock.listen(1)
        self._conn, addr = self._sock.accept()
        logger.info(f"Connection on {self._addr}")

    def _read(self):
        return self._conn.recv(64)

    def _send(self, data):
        num_written = self._conn.send(data)
        if num_written != len(data):
            logger.error(f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                         f" but only sent {num_written} bytes")
        return num_written

    def _close_socket(self):
        self._conn = None
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()
        self._sock = None
        logger.info(f"Closed {self}")

    @abc.abstractmethod
    def _process_data(self, data):
        pass

    def _loop(self):
        try:
            while self._run:
                if self.is_open:
                    try:
                        data = self._read()
                        self._process_data(data)
                    except (ConnectionResetError, OSError) as e:
                        self._close_socket()
                else:
                    self._open()
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            self.close()

    def start(self):
        self._thread.start()

    def close(self):
        try:
            self._close_socket()
        except Exception:
            pass
        finally:
            if os.path.exists(self._addr):
                os.unlink(self._addr)

    def __str__(self):
        return self._addr


class LedSocket(Resource):
    """
    @brief      A mocked version of the LED handler.
    """

    def __init__(self, sock_addr):
        super().__init__('LED', sock_addr, (0, 0, 50, 1))
        self._set_color(BLACK)

    def _set_color(self, color):
        curses_color = curses.color_pair(color.to_term_color())
        self._window.clear()
        self._window.addstr(f"LED Color: {color}", curses_color)
        self._window.noutrefresh()

    def _process_data(self, data):
        self._set_color(Color.from_bytes(data))


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

    def __init__(self, sock_addr):
        super().__init__('LCD', sock_addr, (0, 1, 0, 0))

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
            if len(args) == num_args:
                cmd_func(self, *args)  # Call the function with the args
            else:
                logger.error(f"Expected {num_args} args, got {len(args)}: {format_bytes(data)}")
        else:
            # Data is just text, write to the screen
            s = ''.join(decode_byte(b) for b in data)
            self._write_str(s)


class KeepaliveSocket(Resource):
    def __init__(self, sock_addr):
        super().__init__('Keepalive', sock_addr, None)

    def _process_data(self, data):
        self._send(b'\x01')


def update_window():
    while True:
        curses.doupdate()
        time.sleep(0.05)


def main(stdscr):
    curses.curs_set(0)  # Hide the cursor

    # Add curses colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(1, curses.COLORS):
        curses.init_pair(i, i, -1)  # Background is always blank

    resources = [
        LedSocket(args.led_socket),
        LcdSocket(args.lcd_socket),
        KeepaliveSocket(args.keepalive_socket),
    ]

    try:
        # Start each resource
        for res in resources:
            res.start()

        curses_thread = Thread(target=update_window, name='Curses-Thread', daemon=True)
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
    parser = argparse.ArgumentParser("Mock LED/LCD display for debugging the client/server")
    parser.add_argument('--led-socket', default='/tmp/cc_led.sock',
                        help="Socket to receive LCD data on")
    parser.add_argument('--lcd-socket', default='/tmp/cc_lcd.sock',
                        help="Socket to receive LCD data on")
    parser.add_argument('--keepalive-socket', default='/tmp/cc_keepalive.sock',
                        help="Socket to send keepalive data on")
    args = parser.parse_args()

    curses.wrapper(main)
