import abc
import curses
import itertools
import logging.config
import redis
import signal
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


def format_bytes(data):
    return " ".join("{:02x}".format(b) for b in data)


class Resource:
    def __init__(self, redis_client, pubsub, dimensions, sub_channel):
        self._redis = redis_client
        self._pubsub = pubsub
        self._pubsub.subscribe(**{sub_channel: self._on_pub})

        x, y, width, height = dimensions
        self._window = curses.newwin(height, width, y, x)

    @abc.abstractmethod
    def _on_pub(self, msg):
        pass


class Led(Resource):
    """
    @brief      A mocked version of the LED handler.
    """

    _COLOR_KEY = "reducer:led_color"

    def __init__(self, *args, **kwargs):
        super().__init__(
            dimensions=(0, 0, 50, 1), sub_channel="r2d:led", *args, **kwargs
        )
        self._set_color(BLACK)

    def _on_pub(self, msg):
        # Fetch the correct color from Redis and set it
        color = Color.from_bytes(self._redis.get(__class__._COLOR_KEY))
        self._set_color(color)

    def _set_color(self, color):
        curses_color = curses.color_pair(color.to_term_color())
        self._window.clear()
        self._window.addstr(f"LED Color: {color}", curses_color)
        self._window.noutrefresh()


_lcd_commands = {}


class Lcd(Resource):
    """
    @brief      Where the magic happens for mocking the LCD.
    """

    _COMMAND_QUEUE_KEY = "reducer:lcd_commands"

    def command(code, num_args=0):
        def inner(func):
            def wrapper(*args):
                func(*args)

            _lcd_commands[code] = (num_args, func)
            return wrapper

        return inner

    def __init__(self, *args, **kwargs):
        super().__init__(
            dimensions=(0, 1, 0, 0), sub_channel="r2d:lcd", *args, **kwargs
        )

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
        self._current_char_bank = self._custom_chars[0]

        self._width, self._height = 20, 4
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
        self._window.bkgd(" ", color_pair)
        self._window.noutrefresh()

    @command(CMD_CURSOR_POS, 2)
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
        # We can't do anything with the custom chars, so don't saving them
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

        # Data is a list of bytes objects, of varying lengths. Build a flat
        # iterator of ints so we can process each command one at a time.
        byte_buffer = itertools.chain.from_iterable(data)

        # Iterate through the iterator
        for first_byte in byte_buffer:
            if first_byte == SIG_COMMAND:
                # Data is a command, grab the command byte then the args
                cmd = next(byte_buffer)  # Get the command byte

                try:
                    # Figure out how many args we want
                    num_args, cmd_func = _lcd_commands[cmd]
                except KeyError:
                    logger.error(
                        f"Unknown command {hex(cmd)} in {format_bytes(data)}"
                    )
                # Grab the next n bytes off the buffer
                args = (next(byte_buffer) for _ in range(num_args))
                cmd_func(self, *args)  # Call the function with the args
            else:
                # Data is just text, read one byte from the buffer and write
                # it to screen
                self._write_str(decode_byte(first_byte))

    def _on_pub(self, msg):
        try:
            # Get all data elements from the command queue in Redis, then delete
            # the queue. Doing this in a pipeline makes it atomic/consecutive,
            # so there can't be any race conditions.
            p = self._redis.pipeline()
            p.lrange(__class__._COMMAND_QUEUE_KEY, 0, -1)
            p.delete(__class__._COMMAND_QUEUE_KEY)
            data, _ = p.execute()

            self._process_data(data)
        except Exception:
            logger.error(traceback.format_exc())


class Keepalive(Thread):

    _KEEPALIVE_KEY = "reducer:keepalive"
    _KEEPALIVE_CHANNEL = "r2d:keepalive"

    def __init__(self, redis_client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis = redis_client
        self._shutdown = Event()

    @property
    def should_run(self):
        return not self._shutdown.is_set()

    def stop(self):
        self._shutdown.set()

    def run(self):
        logger.info("Keepalive started")
        while self.should_run:
            # Update
            self._redis.set(__class__._KEEPALIVE_KEY, b"\x01")
            self._redis.publish(__class__._KEEPALIVE_CHANNEL, b"")
            time.sleep(1)
        logger.info("Keepalive stopped")


class SozeDisplay:
    def __init__(self, redis_url):
        redis_client = redis.from_url(redis_url)
        self._pubsub = redis_client.pubsub()

        self._should_run = True
        self._keepalive = Keepalive(redis_client)
        Led(redis_client, self._pubsub)
        Lcd(redis_client, self._pubsub)

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
        logger.info("Starting...")
        try:
            # Start threads
            self._keepalive.start()
            self._pubsub_thread = self._pubsub.run_in_thread()

            # Constantly refresh curses, wait for Ctrl+c
            while self._should_run:
                curses.doupdate()
                time.sleep(0.1)
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            self._stop_threads()

    def _stop(self):
        logger.info("Stopping...")
        self._should_run = False

    def _stop_threads(self):
        self._pubsub_thread.stop()  # Will unsub from all channels
        self._keepalive.stop()
