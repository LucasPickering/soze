#!/usr/bin/env python3

import argparse
import serial
from enum import Enum


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

    def __write(self, data):
        """
        @brief      Writes the given bytes to the serial stream. The given data must be a bytes-like
                    object.

        @param      self  The object
        @param      data  The data (must be bytes-like)

        @return     the number of bytes written
        """
        return self.ser.write(data)

    def __send_command(self, command, *args):
        """
        @brief      Sends the given command to the LCD, with the given arguments.

        @param      self     The object
        @param      command  The command to send
        @param      args     The arguments for the command (if any)

        @return     None
        """
        data_bytes = bytes([self.SIG_COMMAND, command]) + bytes(args)
        self.__write(data_bytes)
        # self.ser.flush()  # Wait for all the serial signals to be sent

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

    def set_color(self, red, green, blue):
        """
        @brief      Sets the color of the LCD.

        @param      self   The object
        @param      red    The red value [0, 255]
        @param      green  The green value [0, 255]
        @param      blue   The blue value [0, 255]

        @return     None
        """
        self.__send_command(self.CMD_COLOR, red, green, blue)

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
            return ''

        lines = [line[:self.width] for line in text.splitlines()[:self.height]]

        self.cursor_home()  # Move the cursor to (1,1) before we start writing
        for y in range(self.height):
            for x in range(self.width):
                old_char = self.__get_char_at(self.lines, x, y)
                new_char = self.__get_char_at(lines, x, y)

                # If this char changed, update it. Otherwise, just advance to the next one.
                if old_char != new_char:
                    # print("{}@({},{})".format(new_char, x, y))
                    self.__write(new_char.encode())
                else:
                    self.move_cursor_forward()
        self.lines = lines

    def stop(self):
        """
        @brief      Closes the serial connection with the LCD.

        @param      self  The object

        @return     None
        """
        self.ser.flush()
        self.ser.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help="Serial port for the LCD")
    args = parser.parse_args()

    lcd = Lcd(args.port)
    # TODO implement debugging stuff here


if __name__ == '__main__':
    main()
