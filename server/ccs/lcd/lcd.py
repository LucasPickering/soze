import serial
from enum import Enum

# Custom chars (e.g. the small blocks used to make big chars) are defined here
# Each character box is 5x8, represented as 8 5-bit lines
CUSTOM_CHARS = {
    0x00: [0b00000, 0b00000, 0b00000, 0b00000, 0b00011, 0b01111, 0b01111, 0b11111],
    0x01: [0b00000, 0b00000, 0b00000, 0b00000, 0b11000, 0b11110, 0b11110, 0b11111],
    0x02: [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111, 0b11111],
    0x03: [0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b01111, 0b01111, 0b00011],
    0x04: [0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11110, 0b11110, 0b11000],
}

# Aliases for the small characters used to make big characters
HBR = '\x00'  # Half-bottom right
HBL = '\x01'  # Half-bottom left
BOT = '\x02'  # Half-bottom
FBR = '\x03'  # Full-bottom right
FBL = '\x04'  # Full-bottom left
FUL = '\xff'  # Full rectangle
EMT = ' '     # Empty (space)

# Character arrays for big characters
BIG_CHARS = {
    '0': [HBR + BOT + HBL,
          FUL + EMT + FUL,
          FBR + BOT + FBL],

    '1': [BOT + HBL + EMT,
          EMT + FUL + EMT,
          BOT + FUL + BOT],

    '2': [HBR + BOT + HBL,
          HBR + BOT + FBL,
          FBR + BOT + BOT],

    '3': [HBR + BOT + HBL,
          EMT + BOT + FUL,
          BOT + BOT + FBL],

    '4': [BOT + EMT + BOT,
          FBR + BOT + FUL,
          EMT + EMT + FUL],

    '5': [BOT + BOT + BOT,
          FUL + BOT + HBL,
          BOT + BOT + FBL],

    '6': [HBR + BOT + HBL,
          FUL + BOT + HBL,
          FBR + BOT + FBL],

    '7': [BOT + BOT + BOT,
          EMT + HBR + FBL,
          EMT + FUL + EMT],

    '8': [HBR + BOT + HBL,
          FUL + BOT + FUL,
          FBR + BOT + FBL],

    '9': [HBR + BOT + HBL,
          FBR + BOT + FUL,
          EMT + EMT + FUL],

    ':': [FUL,
          EMT,
          FUL],

    ' ': [EMT,
          EMT,
          EMT]
}

BAUD_RATE = 9600

# Special signals for the controller
SIG_COMMAND = 0xfe
CMD_CLEAR = 0x58
CMD_BACKLIGHT_ON = 0x42
CMD_BACKLIGHT_OFF = 0x46
CMD_SIZE = 0xd1
CMD_SPLASH_TEXT = 0x40
CMD_BRIGHTNESS = 0x98
CMD_CONTRAST = 0x91
CMD_COLOR = 0xd0
CMD_AUTOSCROLL_ON = 0x51
CMD_AUTOSCROLL_OFF = 0x52
CMD_UNDERLINE_CURSOR_ON = 0x4a
CMD_UNDERLINE_CURSOR_OFF = 0x4b
CMD_BLOCK_CURSOR_ON = 0x53
CMD_BLOCK_CURSOR_OFF = 0x54
CMD_CURSOR_HOME = 0x48
CMD_CURSOR_POS = 0x47
CMD_CURSOR_FWD = 0x4d
CMD_CURSOR_BACK = 0x4c
CMD_CREATE_CHAR = 0x4e
CMD_SAVE_CUSTOM_CHAR = 0xc1
CMD_LOAD_CHAR_BANK = 0xc0


class CursorMode(Enum):
    off = 1
    underline = 2
    block = 3


class Lcd:

    def __init__(self, serial_port, width, height):
        self._width = width
        self._height = height
        self._ser = self._open_serial(serial_port,
                                      baudrate=BAUD_RATE,
                                      bytesize=serial.EIGHTBITS,
                                      parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE)
        self.set_size(width, height)
        self.clear()
        self.set_autoscroll(False)  # Fugg that
        self.on()
        self._lines = [''] * height  # Screen starts blank

        # Register custom characters
        for index, char in CUSTOM_CHARS.items():
            self.create_char(0, index, char)
        self.load_char_bank(0)

    def _open_serial(self, serial_port, **kwargs):
        return serial.Serial(serial_port, **kwargs)

    def _write(self, data, flush=False):
        """
        @brief      Writes the given bytes to the serial stream. The given data must be a bytes-like
                    object.

        @param      self   The object
        @param      data   The data (must be bytes-like)
        @param      flush  Whether or not to flush the serial buffer after writing the data

        @return     the number of bytes written
        """
        rv = self._ser.write(data)
        if flush:
            self.flush_serial()
        return rv

    def _send_command(self, command, *args, flush=False):
        """
        @brief      Sends the given command to the LCD, with the given arguments.

        @param      self     The object
        @param      command  The command to send
        @param      args     The arguments for the command (if any)

        @return     None
        """
        def to_bytes(d):
            if type(d) is int:
                return bytes([d])
            elif type(d) is str:
                return d.encode()
            elif type(d) is bytes:
                return d
            return b''

        arg_bytes_list = [to_bytes(arg) for arg in args]
        joined_bytes = b''.join(arg_bytes_list)
        all_bytes = bytes([SIG_COMMAND, command]) + joined_bytes
        self._write(all_bytes, flush)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def flush_serial(self):
        """
        @brief      Flushes the serial buffer, i.e. waits until everything in the buffer sends.

        @param      self  The object

        @return     None
        """
        self._ser.flush()

    def clear(self):
        """
        @brief      Clears all text on the screen.

        @param      self  The object

        @return     None
        """
        self._send_command(CMD_CLEAR)

    def on(self):
        """
        @brief      Turns the display on., restoring saved brightness, contrast, text and color.

        @param      self  The object

        @return     None
        """
        # The on command takes an arg for how long to stay on, but it's actually ignored.
        self._send_command(CMD_BACKLIGHT_ON, 0)

    def off(self):
        """
        @brief      Turns the display off. Brightness, contrast, text, and color are saved.

        @param      self  The object

        @return     None
        """
        self._send_command(CMD_BACKLIGHT_OFF)

    def set_size(self, width, height):
        """
        @brief      Configures the size of the LCD. Only needs to be called once ever, and the LCD
                    will remember its size.

        @param      self    The object
        @param      width   The width of the LCD (in characters)
        @param      height  The height of the LCD (in characters)

        @return     None
        """
        self._send_command(CMD_SIZE, width, height)

    def set_splash_text(self, splash_text):
        """
        @brief      Sets the splash text, which is displayed when the LCD boots.

        @param      self         The object
        @param      splash_text  The splash text

        @return     None
        """
        self._send_command(CMD_SPLASH_TEXT, splash_text)

    def set_brightness(self, brightness):
        """
        @brief      Sets the brightness of the LCD.

        @param      self        The object
        @param      brightness  The brightness [0, 255]

        @return     None
        """
        self._send_command(CMD_BRIGHTNESS, brightness)

    def set_contrast(self, contrast):
        """
        @brief      Sets the contrast of the LCD

        @param      self      The object
        @param      contrast  The contrast [0, 255]

        @return     None
        """
        self._send_command(CMD_CONTRAST, contrast)

    def set_color(self, color):
        """
        @brief      Sets the color of the LCD.

        @param      self   The object
        @param      red    The red value [0, 255]
        @param      green  The green value [0, 255]
        @param      blue   The blue value [0, 255]

        @return     None
        """
        self._send_command(CMD_COLOR, color.red, color.green, color.blue)

    def set_autoscroll(self, enabled):
        """
        @brief      Enables or disables autoscrolling. When autoscrolling is enabled, the LCD
                    automatically scrolls down when the text is too long to fit on one screen.

        @param      self     The object
        @param      enabled  Whether or not to enable autoscroll [True or False]

        @return     None
        """
        if enabled:
            self._send_command(CMD_AUTOSCROLL_ON)
        else:
            self._send_command(CMD_AUTOSCROLL_OFF)

    def set_cursor_mode(self, cursor_mode):
        """
        @brief      Sets the cursor mode. Options (specified the CursorMode class) are off,
                    underline, and block.

        @param      self         The object
        @param      cursor_mode  The cursor mode (see CursorMode class)

        @return     None
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

        @param      self  The object

        @return     None
        """
        self._send_command(CMD_CURSOR_HOME)

    def set_cursor_pos(self, x, y):
        """
        @brief      Sets the position of the cursor. The top-left corner is (1,1). X increases going
                    right, y increases going down.

        @param      self  The object
        @param      x     The x position of the cursor
        @param      y     The y position of the cursor

        @return     None
        """
        self._send_command(CMD_CURSOR_POS, x, y)

    def move_cursor_forward(self):
        """
        @brief      Moves the cursor forward one position. If it is at the end of the screen, it
        will wrap to (1,1)

        @param      self  The object

        @return     None
        """
        self._send_command(CMD_CURSOR_FWD)

    def move_cursor_back(self):
        """
        @brief      Moves the cursor back one position. If it is at (1,1), it will wrap to the end
        of the screen.

        @param      self  The object

        @return     None
        """
        self._send_command(CMD_CURSOR_BACK)

    def create_char(self, bank, code, char_bytes):
        self._send_command(CMD_SAVE_CUSTOM_CHAR, bank, code, *char_bytes)

    def load_char_bank(self, bank):
        self._send_command(CMD_LOAD_CHAR_BANK, bank)

    def set_text(self, text):
        """
        @brief      Sets the text on the LCD. Only the characters on the LCD that need to change
                    will be updated.

        @param      self  The object
        @param      text  The text for the LCD, with lines separated by a newline character

        @return     None
        """

        def char_at(lines, x, y):
            try:
                return lines[y][x]
            except IndexError:
                return ' '

        lines = [line[:self._width] for line in text.splitlines()[:self._height]]

        self.cursor_home()  # Move the cursor to (1,1) before we start writing
        for y in range(self._height):
            for x in range(self._width):
                old_char = char_at(self._lines, x, y)
                new_char = char_at(lines, x, y)

                # If this char changed, update it
                if old_char != new_char:
                    self.set_cursor_pos(x + 1, y + 1)
                    self._write(new_char.encode())
        self._lines = lines

    def stop(self):
        """
        @brief      Closes the serial connection with the LCD.

        @param      self  The object

        @return     None
        """
        self.off()
        self.clear()
        self.flush_serial()
        self._ser.close()

    @staticmethod
    def make_big_text(text):
        """
        @brief      Converts the given string into "big text". Big text is text that is three lines
                    high. The return value will be a three-line string reprsenting the given text
                    in "big form."

        @param      text  The text to make big

        @return     The big text.
        """

        def _get_big_char(char):
            try:
                return BIG_CHARS[char]
            except KeyError:
                raise ValueError(f"Unsupported big character: {char}")

        def _add_spaces(line):
            # Add a space after every character, except for spaces (don't double them up)
            result = ''
            for c in line:
                if c != ' ':
                    result += c
                result += ' '
            return result

        def _make_big_line(line):
            line = _add_spaces(line)  # Add some spaces to the line to make it look nicer
            big_chars = [_get_big_char(c) for c in line]
            line_tuples = zip(*big_chars)
            big_lines = [''.join(t) for t in line_tuples]
            return '\n'.join(big_lines)

        lines = text.splitlines()
        return [_make_big_line(line) for line in lines]
