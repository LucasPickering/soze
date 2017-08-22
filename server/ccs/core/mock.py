from ccs.lcd.lcd import Lcd


class MockedSerial:

    def write(self, data):
        pass  # TODO something useful here

    def flush(self):
        pass

    def close(self):
        pass


class MockedLcd(Lcd):
    """
    @brief      A mocked verison of the LCD handler, for testing without the required hardware.
    """

    def __init__(self, serial_port, width=Lcd.DEFAULT_WIDTH, height=Lcd.DEFAULT_HEIGHT):
        self.width = width
        self.height = height
        self.ser = MockedSerial()
        self.set_size(width, height)
        self.clear()
        self.lines = [''] * height  # Screen starts blank


class MockedLed:

    def stop(self):
        self.off()

    def set_color(self, red, green, blue):
        self.red = red

    def off(self):
        self.set_color(0, 0, 0)
