from .helper import *


class Lcd:

    def __init__(self, serial_port, width, height):
        self._width = width
        self._height = height

        import serial  # Import here to all for mocking
        self._ser = serial.Serial(serial_port,
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
