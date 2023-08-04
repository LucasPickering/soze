import abc
import curses
import itertools
import logging.config
import os
import signal
import socket
import time
import traceback
from threading import Event, Thread

from .color import BLACK, Color

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
                "filename": "display.log",
                "mode": "w",
            }
        },
        "loggers": {__name__: {"handlers": ["file"], "level": "DEBUG"}},
    }
)
logger = logging.getLogger(__name__)


# Special signals for the controller
SIG_COMMAND = 0xFE
CMD_CLEAR = 0x58
CMD_BACKLIGHT_ON = 0x42
CMD_BACKLIGHT_OFF = 0x46
CMD_SIZE = 0xD1
CMD_SPLASH_TEXT = 0x40
CMD_BRIGHTNESS = 0x98
CMD_CONTRAST = 0x91
CMD_COLOR = 0xD0
CMD_AUTOSCROLL_ON = 0x51
CMD_AUTOSCROLL_OFF = 0x52
CMD_UNDERLINE_CURSOR_ON = 0x4A
CMD_UNDERLINE_CURSOR_OFF = 0x4B
CMD_BLOCK_CURSOR_ON = 0x53
CMD_BLOCK_CURSOR_OFF = 0x54
CMD_CURSOR_HOME = 0x48
CMD_CURSOR_POS = 0x47
CMD_CURSOR_FWD = 0x4D
CMD_CURSOR_BACK = 0x4C
CMD_CREATE_CHAR = 0x4E
CMD_SAVE_CUSTOM_CHAR = 0xC1
CMD_LOAD_CHAR_BANK = 0xC0


class SozeDisplay:
    def __init__(self):
        self._should_run = True

        self._resources = [Led(), Lcd()]

        # Curses init
        curses.curs_set(0)  # Hide the cursor
        # Add xterm colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, curses.COLORS):
            curses.init_pair(i, i, -1)  # Background is always blank

        # Register exit handlers
        def stop_handler(sig, frame):
            self._stop()

        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)

    def run(self):
        logger.info("Starting main loop...")
        try:
            # Start resources in threads
            for resource in self._resources:
                resource.start()

            # Constantly refresh curses, wait for Ctrl+c
            while self._should_run:
                curses.doupdate()
                time.sleep(0.1)
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            self._stop_threads()
        logger.info("Auf wiedersehen!")

    def _stop(self):
        # This will exit the main while loop, which will then stop the threads
        logger.info("Stopping main loop...")
        self._should_run = False

    def _stop_threads(self):
        logger.info("Stopping threads...")
        for resource in self._resources:
            resource.stop()


class Resource(Thread):
    def __init__(self, name, socket_path, dimensions):
        super().__init__(name=name)
        x, y, width, height = dimensions
        self._shutdown = Event()
        self._window = curses.newwin(height, width, y, x)

        # Remove the socket file if it already exists
        try:
            os.unlink(socket_path)
        except OSError:
            if os.path.exists(socket_path):
                raise
        # Bind to the socket
        self._socket_path = socket_path
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.bind(socket_path)

    @property
    def should_run(self):
        return not self._shutdown.is_set()

    def run(self):
        logger.info(f"Listening on {self._socket_path}...")
        self._socket.listen(0)
        try:
            while self.should_run:
                logger.info("Waiting for client...")
                connection, client_address = self._socket.accept()
                byte_stream = self.get_byte_stream(connection)
                self.process_data(byte_stream)
            logger.info("Stopped listener loop")
        except ConnectionAbortedError:
            logger.info("Connection closed")
        except Exception:
            logger.exception("Error!")
            raise
        # Cleanup
        finally:
            os.unlink(self._socket_path)
            logger.info("Nägemist!")

    def stop(self):
        logger.info("Stopping...")
        self._shutdown.set()
        self._socket.close()

    def get_byte_stream(self, connection):
        logger.info("Client connected")
        while self.should_run:
            data = connection.recv(1024)
            if data is None:
                logger.info("Client disconnected")
                return
            yield from data

    @abc.abstractmethod
    def process_data(self, byte_stream):
        """
        Handle data from a generator of bytes. The generator will continually
        produce bytes until the socket closes.
        """
        pass


class Led(Resource):
    """
    @brief      A mocked version of the LED handler.
    """

    def __init__(self):
        super().__init__(
            name="LED", socket_path="/tmp/soze-led", dimensions=(0, 0, 50, 1)
        )
        self._set_color(BLACK)

    def process_data(self, byte_stream):
        # Grab 3 bytes at a time from the stream
        red, green, blue = itertools.islice(byte_stream, 3)
        color = Color(red, green, blue)
        logger.debug(f"Set color to {color}")
        self._set_color(color)

    def _set_color(self, color):
        curses_color = curses.color_pair(color.to_term_color())
        self._window.clear()
        self._window.addstr(f"LED Color: {color}", curses_color)
        self._window.noutrefresh()


_lcd_commands = {}
# These characters are hard-coded into the LCD, but aren't in ASCII
EXTRA_CHARS = {
    0xFF: "█",
}
# These characters can be identified by their pixel patterns
KNOWN_CUSTOM_CHARACTERS = {
    # Half-bottom right
    (
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00011,
        0b01111,
        0b01111,
        0b11111,
    ): "▗",
    # Half-bottom left
    (
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b11000,
        0b11110,
        0b11110,
        0b11111,
    ): "▖",
    # Half-bottom
    (
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
    ): "▄",
    # Full-bottom right
    (
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b01111,
        0b01111,
        0b00011,
    ): "▜",
    # Full-bottom left
    (
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11110,
        0b11110,
        0b11000,
    ): "▛",
}


class Lcd(Resource):
    """
    @brief      Where the magic happens for mocking the LCD.
    """

    def command(code, arg_len=None):
        """Register an LCD command"""

        def inner(func):
            def wrapper(*args):
                func(*args)

            # If no arg length is given, count the args on the function
            if arg_len is None:
                arg_len_ = func.__code__.co_argcount - 1  # First arg is self
            else:
                arg_len_ = arg_len
            _lcd_commands[code] = (arg_len_, func)
            logger.debug(
                f"Registered command 0x{code:2x} for {func.__name__}"
                f" ({arg_len_} arg bytes)"
            )
            return wrapper

        return inner

    def __init__(self):
        super().__init__(
            name="LCD", socket_path="/tmp/soze-lcd", dimensions=(0, 1, 0, 0)
        )
        # No custom characters defined by default
        self._custom_chars = {0: {}}
        self._current_char_bank = self._custom_chars[0]

        self._width, self._height = 20, 4
        self._cursor_x, self._cursor_y = 0, 0

    def _cursor_forward(self, n):
        """Move the cursor forward some number of characters"""
        self._set_cursor_pos(self._cursor_x + n, self._cursor_y)

    def _set_cursor_pos(self, x, y):
        # Adjust down for the LCD backpack's 1-based indexing
        better_x = x - 1
        better_y = y - 1

        # Wrap on x and y
        wrapped_x = better_x % self._width
        wrapped_y = (int(better_x / self._width) + better_y) % self._height

        # Shift back for 1-based indexing
        self._cursor_x = wrapped_x + 1
        self._cursor_y = wrapped_y + 1

    @command(CMD_CLEAR)
    def _cmd_clear(self):
        logger.debug("Clearing LCD")
        self._window.clear()
        self._window.border()
        self._window.noutrefresh()

    @command(CMD_BACKLIGHT_ON)
    def _cmd_backlight_on(
        self, timeout
    ):  # timeout is unused in Adafruit's driver
        logger.debug("Backlight enabled")
        pass  # TODO

    @command(CMD_BACKLIGHT_OFF)
    def _cmd_backlight_off(self):
        logger.debug("Backlight disabled")
        pass  # TODO

    @command(CMD_SIZE)
    def _cmd_set_size(self, width, height):
        logger.debug(f"Set LCD size to {width}x{height}")
        self._width, self._height = width, height
        self._window.resize(height + 2, width + 2)  # padding for border
        self._window.border()
        self._window.noutrefresh()

    @command(CMD_CONTRAST)
    def _cmd_set_contrast(self, contrast):
        logger.debug(f"Set contrast to {contrast}")
        pass

    @command(CMD_BRIGHTNESS)
    def _cmd_set_brightness(self, brightness):
        logger.debug(f"Set brightness to {brightness}")
        pass

    @command(CMD_COLOR)
    def _cmd_set_color(self, red, green, blue):
        color = Color(red, green, blue)
        logger.debug(f"Set backlight color to {color}")
        color_pair = curses.color_pair(color.to_term_color())
        self._window.bkgd(" ", color_pair)
        self._window.noutrefresh()

    @command(CMD_CURSOR_POS)
    def _cmd_set_cursor_pos(self, x, y):
        logger.debug(f"Set cursor position to ({x}, {y})")
        self._set_cursor_pos(x, y)

    @command(CMD_CURSOR_HOME)
    def _cmd_cursor_home(self):
        logger.debug("Move cursor to home")
        self._set_cursor_pos(1, 1)

    @command(CMD_CURSOR_FWD)
    def _cmd_cursor_forward(self, n):
        logger.debug("Move cursor forward")
        self._cursor_forward(n)

    @command(CMD_CURSOR_BACK)
    def _cmd_cursor_back(self, n):
        logger.debug("Move cursor back")
        self._set_cursor_pos(self._cursor_x - n, self._cursor_y)

    @command(CMD_SAVE_CUSTOM_CHAR, arg_len=10)  # bank + code + 8 char bytes
    def _cmd_save_custom_char(self, bank, code, *char_bytes):
        # Match custom char to a known char based on the bit pattern
        try:
            char = KNOWN_CUSTOM_CHARACTERS[char_bytes]
            logger.error(f"Custom character `{char}` saved to code 0x{code:2x}")
        except KeyError:
            char = "�"
            logger.error(f"Unknown custom character saved to code 0x{code:2x}")
        self._custom_chars[bank][code] = char

    @command(CMD_LOAD_CHAR_BANK)
    def _cmd_load_char_bank(self, bank):
        logger.debug(f"Load character bank {bank}")
        self._current_char_bank = self._custom_chars[bank]

    @command(CMD_AUTOSCROLL_ON)
    def _cmd_autoscroll_on(self):
        logger.debug("Enable auto-scroll")

    @command(CMD_AUTOSCROLL_OFF)
    def _cmd_autoscroll_off(self):
        logger.debug("Disable auto-scroll")

    def _write_str(self, s):
        logger.debug(f"Writing text `{s}`")
        self._window.addstr(self._cursor_y, self._cursor_x, s)
        self._window.noutrefresh()
        self._cursor_forward(len(s))

    def process_data(self, byte_stream):
        def decode_char(b):
            # First check custom characters
            if b in self._current_char_bank:
                return self._current_char_bank[b]
            # Then check hard-coded extra characters
            elif b in EXTRA_CHARS:
                return EXTRA_CHARS[b]
            # Then check if it's ASCII
            elif b < 128:
                return chr(b)
            else:
                logger.error(f"Unknown text byte 0x{b:2x}")
                return "�"

        # Iterate through the bytes, and handle one or more commands
        for first_byte in byte_stream:
            if first_byte == SIG_COMMAND:
                # Data is a command, grab the command byte then the args
                cmd_byte = next(byte_stream)  # Get the command byte

                try:
                    # Figure out how many args we want
                    num_args, cmd_func = _lcd_commands[cmd_byte]
                except KeyError:
                    logger.error(f"Unknown command {hex(cmd_byte)}")
                # Grab the next n bytes off the buffer
                args = itertools.islice(byte_stream, num_args)
                cmd_func(self, *args)  # Call the function with the args
            else:
                # Data is just text, read one byte from the buffer and write
                # it to screen
                self._write_str(decode_char(first_byte))
