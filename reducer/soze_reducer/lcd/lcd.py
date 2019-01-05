import itertools

from soze_reducer import logger
from soze_reducer.core.color import BLACK
from soze_reducer.core.resource import ReducerResource
from .helper import (
    CMD_AUTOSCROLL_OFF,
    CMD_AUTOSCROLL_ON,
    CMD_BACKLIGHT_OFF,
    CMD_BACKLIGHT_ON,
    CMD_BLOCK_CURSOR_OFF,
    CMD_BLOCK_CURSOR_ON,
    CMD_BRIGHTNESS,
    CMD_CLEAR,
    CMD_COLOR,
    CMD_CONTRAST,
    CMD_CURSOR_BACK,
    CMD_CURSOR_FWD,
    CMD_CURSOR_HOME,
    CMD_CURSOR_POS,
    CMD_LOAD_CHAR_BANK,
    CMD_SAVE_CUSTOM_CHAR,
    CMD_SIZE,
    CMD_SPLASH_TEXT,
    CMD_UNDERLINE_CURSOR_OFF,
    CMD_UNDERLINE_CURSOR_ON,
    CUSTOM_CHARS,
    SIG_COMMAND,
    CursorMode,
    diff_text,
)
from .mode import LcdMode


class Lcd(ReducerResource):

    _DEFAULT_WIDTH = 20
    _DEFAULT_HEIGHT = 4
    _COMMAND_QUEUE_KEY = "reducer:lcd_commands"

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            name="LCD",
            settings_key_prefix="lcd",
            sub_channel="a2r:lcd",
            pub_channel="r2d:lcd",
            mode_class=LcdMode,
            **kwargs,
        )
        # Declare fields
        self._width = __class__._DEFAULT_WIDTH
        self._height = __class__._DEFAULT_HEIGHT
        self._color = None
        self._lines = None
        # Used to queue up bytes and send them to Redis in bulk
        self._command_queue = None

    def _after_init(self):
        # Initiate a transaction. Only one Redis push will occur, at the end.
        with self:
            self.set_size(self.width, self.height, True)
            self.set_color(BLACK)

            self.clear()
            self.set_autoscroll(False)  # Fugg that
            self.on()

            # Register custom characters
            for index, char in CUSTOM_CHARS.items():
                self.create_char(0, index, char)
            self.load_char_bank(0)

    def _before_stop(self):
        """
        @brief      Turns the LCD off and clears it.
        """
        self.off()
        self.clear()

    def _get_default_values(self):
        return (BLACK, "")

    def _get_values(self):
        return (
            self._mode.get_color(self._settings),
            self._mode.get_text(self._settings),
        )

    def _apply_values(self, color, text):
        # Initiate a transaction. Only one Redis push will occur, at the end.
        with self:
            self.set_color(color)
            self.set_text(text)

    def _queue_bytes(self, *data):
        # Add the given data to the queue
        try:
            self._command_queue += data
        except TypeError:
            raise ValueError("No command queue exists")

    def _send_command(self, command, *args):
        """
        @brief      Sends the given command to the LCD, with the given arguments

        @param      command  The command to send
        @param      args     The arguments for the command (if any)
        """
        all_bytes = bytes([SIG_COMMAND, command] + list(args))
        self._queue_bytes(all_bytes)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def clear(self):
        """
        @brief      Clears all text on the screen.
        """
        self._send_command(CMD_CLEAR)

    def on(self):
        """
        @brief      Turns the display on, restoring saved brightness, contrast,
                    text and color.
        """
        # The ON command takes an arg for how long to stay on,
        # but it's actually ignored.
        self._send_command(CMD_BACKLIGHT_ON, 0)

    def off(self):
        """
        @brief      Turns the display off. Brightness, contrast, text,
                    and color are saved.
        """
        self._send_command(CMD_BACKLIGHT_OFF)

    def set_size(self, width, height, force_update=False):
        """
        @brief      Configures the size of the LCD. Only needs to be called
                    once ever, and the LCD will remember its size.

        @param      width   The width of the LCD (in characters)
        @param      height  The height of the LCD (in characters)
        """
        if force_update or self.width != width or self.height != height:
            self._width, self._height = width, height
            self._send_command(CMD_SIZE, width, height)
            self._lines = [""] * height  # Resize the text buffer

    def set_splash_text(self, splash_text):
        """
        @brief      Sets the splash text, which is displayed when the LCD boots.

        @param      splash_text  The splash text
        """
        self._send_command(CMD_SPLASH_TEXT, splash_text.encode())

    def set_brightness(self, brightness):
        """
        @brief      Sets the brightness of the LCD.

        @param      brightness  The brightness [0, 255]
        """
        self._send_command(CMD_BRIGHTNESS, brightness)

    def set_contrast(self, contrast):
        """
        @brief      Sets the contrast of the LCD

        @param      contrast  The contrast [0, 255]
        """
        self._send_command(CMD_CONTRAST, contrast)

    def set_color(self, color):
        """
        @brief      Sets the color of the LCD.

        @param      red    The red value [0, 255]
        @param      green  The green value [0, 255]
        @param      blue   The blue value [0, 255]
        """
        # Make sure the value is actually changing, to prevent unnecessary
        # writes to Redis
        if color != self._color:
            self._color = color
            self._send_command(CMD_COLOR, color.red, color.green, color.blue)

    def set_autoscroll(self, enabled):
        """
        @brief      Enables or disables autoscrolling. When autoscrolling is
                    enabled, the LCD automatically scrolls down when the text
                    is too long to fit on one screen.

        @param      enabled  Whether or not to enable autoscroll [True or False]
        """
        if enabled:
            self._send_command(CMD_AUTOSCROLL_ON)
        else:
            self._send_command(CMD_AUTOSCROLL_OFF)

    def set_cursor_mode(self, cursor_mode):
        """
        @brief      Sets the cursor mode. Options (specified via the
                    CursorMode class) are off, underline, and block.

        @param      cursor_mode  The cursor mode (see CursorMode class)
        """
        if cursor_mode == CursorMode.off:
            self._send_command(CMD_UNDERLINE_CURSOR_OFF)
            self._send_command(CMD_BLOCK_CURSOR_OFF)
        elif cursor_mode == CursorMode.underline:
            self._send_command(CMD_UNDERLINE_CURSOR_ON)
        elif cursor_mode == CursorMode.block:
            self._send_command(CMD_BLOCK_CURSOR_ON)

    def cursor_home(self):
        """
        @brief      Moves the cursor to the (1,1) position.
        """
        self._send_command(CMD_CURSOR_HOME)

    def set_cursor_pos(self, x, y):
        """
        @brief      Sets the position of the cursor. The top-left corner is
                    (1,1). X increases going right, y increases going down.

        @param      x     The x position of the cursor
        @param      y     The y position of the cursor
        """
        self._send_command(CMD_CURSOR_POS, x, y)

    def move_cursor_forward(self):
        """
        @brief      Moves the cursor forward one position. If it is at the end
                    of the screen, it will wrap to (1,1).
        """
        self._send_command(CMD_CURSOR_FWD)

    def move_cursor_back(self):
        """
        @brief      Moves the cursor back one position. If it is at (1,1), it
                    will wrap to the end of the screen.
        """
        self._send_command(CMD_CURSOR_BACK)

    def create_char(self, bank, code, char_bytes):
        """
        @brief      Creates a custom character in the given bank, with the
                    given alias (code) and given pattern.
        """
        self._send_command(CMD_SAVE_CUSTOM_CHAR, bank, code, *char_bytes)

    def load_char_bank(self, bank):
        """
        @brief      Loads the custom character bank with the given index.
        """
        self._send_command(CMD_LOAD_CHAR_BANK, bank)

    def set_text(self, text):
        """
        @brief      Sets the text on the LCD. Only the characters on the LCD
                    that need to change will be updated.

        @param      text  The text for the LCD, with lines separated by a
                        newline character
        """

        def encode_str(s):
            # UTF-8 encodes 128+ as two bytes but we use ord to get just one
            # byte, [0, 255]
            return bytes(ord(c) for c in s)

        lines = [
            line[: self.width] for line in text.splitlines()[: self.height]
        ]
        diff = diff_text(self._lines, lines)

        # Build a list of bytes we want to write
        to_write = []
        for (x, y), s in diff.items():
            # Move the cursor to the right spot (the LCD coords are 1-based)
            self.set_cursor_pos(x + 1, y + 1)
            to_write.append(encode_str(s))

        self._lines = lines
        self._queue_bytes(*to_write)  # Add the text to the byte queue

    def __enter__(self):
        # Initialize a command queue
        if self._command_queue is not None:
            raise ValueError("Command queue already exists")
        self._command_queue = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If we exited cleanly, push the queued bytes to Redis
        try:
            if not exc_type:
                # Squash all the queued bytes into one long bytes object
                to_push = bytes(
                    itertools.chain.from_iterable(self._command_queue)
                )
                if to_push:
                    self._redis.rpush(__class__._COMMAND_QUEUE_KEY, to_push)
        finally:
            self._command_queue = None
