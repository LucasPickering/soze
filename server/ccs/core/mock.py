import curses

from ccs import logger
from .color import BLACK
from ccs.lcd import lcd

_stdscr = curses.initscr()


class MockedLed:
    """
    @brief      A mocked version of the LED handler.
    """

    def __init__(self):
        self._window = curses.newwin(1, 50, 0, 0)

    def set_color(self, color):
        self._window.clear()
        self._window.addstr(0, 0, f'LED Color: {color}')
        self._window.refresh()

    def stop(self):
        self.off()
        curses.endwin()  # Kill the curses window

    def off(self):
        self.set_color(BLACK)


class MockedLcd(lcd.Lcd):
    """
    @brief      A mocked verison of the LCD handler, for testing without the required hardware.
                This is pretty minimal, most of the hard work goes on in MockedSerial.
    """
    _START_LINE = 1

    def __init__(self, serial_port, width=lcd.DEFAULT_WIDTH, height=lcd.DEFAULT_HEIGHT):
        self._width = width
        self._height = height

        # Init the curses window
        self._window = curses.newwin(self._height + 2, self._width + 2, 1, 0)
        self._window.border()
        self._window.refresh()

        self._ser = MockedSerial(self._window)
        self._lines = [''] * height  # Screen starts blank
        self.set_size(width, height)
        self.clear()

    def stop(self):
        super().stop()
        curses.endwin()  # REALLY kill the curses window


class MockedSerial:
    """
    @brief      Where the magic happens for mocking the LCD.
    """

    def __init__(self, window):
        self._window = window
        self._set_size(1, 1)
        self._set_cursor_pos(1, 1)  # Yes, (1, 1) is the origin. Fuck Adafruit.

        # Unfortunately this has to be initialized where self is available
        self._cmd_funcs = {
            lcd.CMD_CLEAR: lambda self, args: self._clear(),
            lcd.CMD_BACKLIGHT_ON: lambda self, args: None,
            lcd.CMD_BACKLIGHT_OFF: lambda self, args: None,
            lcd.CMD_SIZE: lambda self, args: self._set_size(args[0], args[1]),
            lcd.CMD_SPLASH_TEXT: lambda self, args: None,
            lcd.CMD_BRIGHTNESS: lambda self, args: None,
            lcd.CMD_CONTRAST: lambda self, args: None,
            lcd.CMD_COLOR: lambda self, args: None,
            lcd.CMD_AUTOSCROLL_ON: lambda self, args: None,  # Not supporting (always off)
            lcd.CMD_AUTOSCROLL_OFF: lambda self, args: None,
            lcd.CMD_UNDERLINE_CURSOR_ON: lambda self, args: None,
            lcd.CMD_UNDERLINE_CURSOR_OFF: lambda self, args: None,
            lcd.CMD_BLOCK_CURSOR_ON: lambda self, args: None,
            lcd.CMD_BLOCK_CURSOR_OFF: lambda self, args: None,
            lcd.CMD_CURSOR_HOME: lambda self, args: self._set_cursor_pos(1, 1),
            lcd.CMD_CURSOR_POS: lambda self, args: self._set_cursor_pos(args[0], args[1]),
            lcd.CMD_CURSOR_FWD: lambda self, args: self._cursor_fwd(),
            lcd.CMD_CURSOR_BACK: lambda self, args: self._cursor_back(),
            lcd.CMD_CREATE_CHAR: lambda self, args: None,
            lcd.CMD_SAVE_CUSTOM_CHAR: lambda self, args: None,
            lcd.CMD_LOAD_CHAR_BANK: lambda self, args: None,
        }

    def _set_size(self, width, height):
        self._width = width
        self._height = height

    def _set_cursor_pos(self, x, y):
        if self._width == 0 or self._height == 0:
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

    def _clear(self):
        self._window.clear()
        self._window.border()  # Put the pretty border back
        self._window.refresh()

    def write(self, data):
        if len(data) == 0:
            return
        if data[0] == lcd.SIG_COMMAND:
            cmd = data[1]
            args = data[2:]
            try:
                # logger.debug(hex(cmd))
                cmd_func = self._cmd_funcs[cmd]  # Get the function for this command
            except KeyError:
                raise ValueError(f"Unknown command: 0x{cmd:02x}")
            cmd_func(self, args)  # Call the function with the args
        else:
            # Data is just text, write to the screen
            logger.debug(f"Writing {data} to screen")
            for b in data:
                self._window.addch(self._cursor_y, self._cursor_x, b)
                self._cursor_fwd()  # Advance the cursor after every char
            self._window.refresh()

    def flush(self):
        pass

    def close(self):
        pass
