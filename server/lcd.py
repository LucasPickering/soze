#!/usr/bin/env python3

import argparse
import serial
from enum import Enum

# Custom chars (e.g. the small blocks used to make big chars) are defined here
# Each character box is 5x8, represented as 8 5-bit lines
CUSTOM_CHARS = {
    0: [0b00000, 0b00000, 0b00000, 0b00000, 0b00011, 0b01111, 0b01111, 0b11111],
    1: [0b00000, 0b00000, 0b00000, 0b00000, 0b11000, 0b11110, 0b11110, 0b11111],
    2: [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111, 0b11111],
    3: [0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b01111, 0b01111, 0b00011],
    4: [0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11110, 0b11110, 0b11000],
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


def make_big_text(text):
    """
    @brief      Converts the given string into "big text". Big text is text that is three lines
                high. The return value will be a three-line string reprsenting the given text
                in "big form."

    @param      text  The text to make big

    @return     The big text.
    """

    def __get_big_char(char):
        try:
            return BIG_CHARS[char]
        except KeyError:
            raise ValueError("Unsupported big character: {}".format(char))

    def __add_spaces(line):
        # Add a space after every character, except for spaces (don't double them up)
        result = ''
        for c in line:
            if c != ' ':
                result += c
            result += ' '
        return result

    def __make_big_line(line):
        line = __add_spaces(line)  # Add some spaces to the line to make it look nicer
        big_chars = [__get_big_char(c) for c in line]
        line_tuples = zip(*big_chars)
        big_lines = [''.join(t) for t in line_tuples]
        return '\n'.join(big_lines)

    lines = text.splitlines()
    return [__make_big_line(line) for line in lines]


class CursorMode(Enum):
    off = 1
    underline = 2
    block = 3


class Lcd:

    BAUD_RATE = 9600

    DEFAULT_WIDTH = 20
    DEFAULT_HEIGHT = 4

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

    def __init__(self, serial_port, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        self.width = width
        self.height = height
        self.serial_port = serial_port
        self.ser = serial.Serial(serial_port,
                                 baudrate=self.BAUD_RATE,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE)
        self.set_size(width, height)
        self.clear()
        self.lines = [''] * height  # Screen starts blank

        # Register custom characters
        for index, char in CUSTOM_CHARS.items():
            self.create_char(0, index, char)
        self.load_char_bank(0)

    def __write(self, data, flush=False):
        """
        @brief      Writes the given bytes to the serial stream. The given data must be a bytes-like
                    object.

        @param      self   The object
        @param      data   The data (must be bytes-like)
        @param      flush  Whether or not to flush the serial buffer after writing the data

        @return     the number of bytes written
        """
        rv = self.ser.write(data)
        if flush:
            self.flush_serial()
        return rv

    def __send_command(self, command, *args, flush=False):
        """
        @brief      Sends the given command to the LCD, with the given arguments.

        @param      self     The object
        @param      command  The command to send
        @param      args     The arguments for the command (if any)

        @return     None
        """
        def __to_bytes(d):
            if type(d) is int:
                return bytes([d])
            elif type(d) is str:
                return d.encode()
            elif type(d) is bytes:
                return d
            return b''

        arg_bytes_list = [__to_bytes(arg) for arg in args]
        joined_bytes = b''.join(arg_bytes_list)
        all_bytes = bytes([self.SIG_COMMAND, command]) + joined_bytes
        self.__write(all_bytes, flush)

    def flush_serial(self):
        """
        @brief      Flushes the serial buffer, i.e. waits until everything in the buffer sends.

        @param      self  The object

        @return     None
        """
        self.ser.flush()

    def clear(self):
        """
        @brief      Clears all text on the screen.

        @param      self  The object

        @return     None
        """
        self.__send_command(self.CMD_CLEAR)

    def on(self):
        """
        @brief      Turns the display on., restoring saved brightness, contrast, text and color.

        @param      self  The object

        @return     None
        """
        # The on command takes an arg for how long to stay on, but it's actually ignored.
        self.__send_command(self.CMD_BACKLIGHT_ON, 0)

    def off(self):
        """
        @brief      Turns the display off. Brightness, contrast, text, and color are saved.

        @param      self  The object

        @return     None
        """
        self.__send_command(self.CMD_BACKLIGHT_OFF)

    def set_size(self, width, height):
        """
        @brief      Configures the size of the LCD. Only needs to be called once ever, and the LCD
                    will remember its size.

        @param      self    The object
        @param      width   The width of the LCD (in characters)
        @param      height  The height of the LCD (in characters)

        @return     None
        """
        self.__send_command(self.CMD_SIZE, width, height)

    def set_splash_text(self, splash_text):
        """
        @brief      Sets the splash text, which is displayed when the LCD boots.

        @param      self         The object
        @param      splash_text  The splash text

        @return     None
        """
        self.__send_command(self.CMD_SPLASH_TEXT, splash_text)

    def set_brightness(self, brightness):
        """
        @brief      Sets the brightness of the LCD.

        @param      self        The object
        @param      brightness  The brightness [0, 255]

        @return     None
        """
        self.__send_command(self.CMD_BRIGHTNESS, brightness)

    def set_contrast(self, contrast):
        """
        @brief      Sets the contrast of the LCD

        @param      self      The object
        @param      contrast  The contrast [0, 255]

        @return     None
        """
        self.__send_command(self.CMD_CONTRAST, contrast)

    def set_color(self, color):
        """
        @brief      Sets the color of the LCD.

        @param      self   The object
        @param      red    The red value [0, 255]
        @param      green  The green value [0, 255]
        @param      blue   The blue value [0, 255]

        @return     None
        """
        self.__send_command(self.CMD_COLOR, color.red, color.green, color.blue)

    def set_autoscroll(self, enabled):
        """
        @brief      Enables or disables autoscrolling. When autoscrolling is enabled, the LCD
                    automatically scrolls down when the text is too long to fit on one screen.

        @param      self     The object
        @param      enabled  Whether or not to enable autoscroll [True or False]

        @return     None
        """
        if enabled:
            self.__send_command(self.CMD_AUTOSCROLL_ON)
        else:
            self.__send_command(self.CMD_AUTOSCROLL_OFF)

    def set_cursor_mode(self, cursor_mode):
        """
        @brief      Sets the cursor mode. Options (specified the CursorMode class) are off,
                    underline, and block.

        @param      self         The object
        @param      cursor_mode  The cursor mode (see CursorMode class)

        @return     None
        """
        if cursor_mode == CursorMode.off:
            self.__send_command(self.CMD_UNDERLINE_CURSOR_OFF)
            self.__send_command(self.CMD_BLOCK_CURSOR_OFF)
        elif cursor_mode == CursorMode.underline:
            self.__send_command(self.CMD_UNDERLINE_CURSOR_ON)
        elif cursor_mode == CursorMode.block:
            self.__send_command(self.CMD_BLOCK_CURSOR_ON)

    def cursor_home(self):
        """
        @brief      Moves the cursor to the (1,1) position.

        @param      self  The object

        @return     None
        """
        self.__send_command(self.CMD_CURSOR_HOME)

    def set_cursor_pos(self, x, y):
        """
        @brief      Sets the position of the cursor. The top-left corner is (1,1). X increases going
                    right, y increases going down.

        @param      self  The object
        @param      x     The x position of the cursor
        @param      y     The y position of the cursor

        @return     None
        """
        self.__send_command(self.CMD_CURSOR_POS, x, y)

    def move_cursor_forward(self):
        """
        @brief      Moves the cursor forward one position. If it is at the end of the screen, it
        will wrap to (1,1)

        @param      self  The object

        @return     None
        """
        self.__send_command(self.CMD_CURSOR_FWD)

    def move_cursor_back(self):
        """
        @brief      Moves the cursor back one position. If it is at (1,1), it will wrap to the end
        of the screen.

        @param      self  The object

        @return     None
        """
        self.__send_command(self.CMD_CURSOR_BACK)

    def create_char(self, bank, index, char_bytes):
        self.__send_command(self.CMD_SAVE_CUSTOM_CHAR, bank, index, *char_bytes)

    def load_char_bank(self, bank):
        self.__send_command(self.CMD_LOAD_CHAR_BANK, bank)

    def set_text(self, text):
        """
        @brief      Sets the text on the LCD. Only the characters on the LCD that need to change
                    will be updated.

        @param      self  The object
        @param      text  The text for the LCD, with lines separated by a newline character

        @return     None
        """

        def __get_char_at(lines, x, y):
            if y < len(lines):
                line = lines[y]
                if x < len(line):
                    return line[x]
            return ' '

        lines = [line[:self.width] for line in text.splitlines()[:self.height]]

        self.cursor_home()  # Move the cursor to (1,1) before we start writing
        for y in range(self.height):
            for x in range(self.width):
                old_char = __get_char_at(self.lines, x, y)
                new_char = __get_char_at(lines, x, y)

                # If this char changed, update it. Otherwise, just advance to the next one.
                if old_char != new_char:
                    self.__write(bytes([ord(new_char)]))
                else:
                    self.move_cursor_forward()
        self.lines = lines

    def stop(self):
        """
        @brief      Closes the serial connection with the LCD.

        @param      self  The object

        @return     None
        """
        self.flush_serial()
        self.ser.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help="Serial port for the LCD")
    args = parser.parse_args()

    lcd = Lcd(args.port)
    # TODO implement debugging stuff here


if __name__ == '__main__':
    main()
