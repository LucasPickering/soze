import curses

from .color import Color, BLACK
from ccs.led.led import Led
from ccs.lcd import lcd

_stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()
for i in range(1, curses.COLORS):
    curses.init_pair(i, i, -1)  # Background is always blank


class CursesLed(Led):
    """
    @brief      A mocked version of the LED handler.
    """

    def __init__(self):
        self._window = curses.newwin(1, 50, 0, 0)

    def set_color(self, color):
        term_color = color.to_term_color()
        self._window.clear()
        self._window.addstr(f'LED Color: {color}', curses.color_pair(term_color))
        self._window.refresh()

    def stop(self):
        self.off()
        curses.endwin()  # Kill the curses window

    def off(self):
        self.set_color(BLACK)


class CursesLcd(lcd.Lcd):
    """
    @brief      A mocked verison of the LCD handler, for testing without the required hardware.
                This is pretty minimal, most of the hard work goes on in MockedSerial.
    """

    def _open_serial(self, serial_port, **kwargs):
        return CursesSerial()


class CursesSerial:
    """
    @brief      Where the magic happens for mocking the LCD.
    """

    _CMD_FUNCS = {
        lcd.CMD_CLEAR: lambda self, args: self._clear(),
        lcd.CMD_BACKLIGHT_ON: lambda self, args: None,
        lcd.CMD_BACKLIGHT_OFF: lambda self, args: None,
        lcd.CMD_SIZE: lambda self, args: self._set_size(*args),
        lcd.CMD_SPLASH_TEXT: lambda self, args: None,
        lcd.CMD_BRIGHTNESS: lambda self, args: None,
        lcd.CMD_CONTRAST: lambda self, args: None,
        lcd.CMD_COLOR: lambda self, args: self._set_color(*args),
        lcd.CMD_AUTOSCROLL_ON: lambda self, args: None,  # Not supporting (always off)
        lcd.CMD_AUTOSCROLL_OFF: lambda self, args: None,
        lcd.CMD_UNDERLINE_CURSOR_ON: lambda self, args: None,
        lcd.CMD_UNDERLINE_CURSOR_OFF: lambda self, args: None,
        lcd.CMD_BLOCK_CURSOR_ON: lambda self, args: None,
        lcd.CMD_BLOCK_CURSOR_OFF: lambda self, args: None,
        lcd.CMD_CURSOR_HOME: lambda self, args: self._set_cursor_pos(1, 1),
        lcd.CMD_CURSOR_POS: lambda self, args: self._set_cursor_pos(*args),
        lcd.CMD_CURSOR_FWD: lambda self, args: self._cursor_fwd(),
        lcd.CMD_CURSOR_BACK: lambda self, args: self._cursor_back(),
        lcd.CMD_CREATE_CHAR: lambda self, args: None,  # This thing is useless
        lcd.CMD_SAVE_CUSTOM_CHAR: lambda self, args: self._save_custom_char(args[0], args[1],
                                                                            args[2:]),
        lcd.CMD_LOAD_CHAR_BANK: lambda self, args: self._load_char_bank(args[0]),
    }

    def __init__(self):
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
        # Init the curses window
        self._window = curses.newwin(0, 0, 1, 0)
        self._border()

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
        self._window.resize(height + 2, width + 2)
        self._border()

    def _set_color(self, red, green, blue):
        term_color = Color(red, green, blue).to_term_color()
        self._window.attrset(term_color)
        # TODO

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
        # We can't do anything with the custom chars, so why save them
        # self._custom_chars[bank][code] = char_bytes
        pass

    def _load_char_bank(self, bank):
        self._current_char_bank = self._custom_chars[bank]

    def write(self, data):
        if len(data) == 0:
            return

        if data[0] == lcd.SIG_COMMAND:
            cmd = data[1]
            args = data[2:]
            try:
                # logger.debug(hex(cmd))
                cmd_func = CursesSerial._CMD_FUNCS[cmd]  # Get the function for this command
            except KeyError:
                raise ValueError(f"Unknown command: 0x{cmd:02x}")
            cmd_func(self, args)  # Call the function with the args
        else:
            # Data is just text, write to the screen
            s = data.decode()
            for code, char in self._current_char_bank.items():
                s = s.replace(chr(code), char)
            self._window.addstr(self._cursor_y, self._cursor_x, s)
            self._window.refresh()

    def flush(self):
        pass

    def close(self):
        curses.endwin()  # Kill the curses window
