from .color import BLACK
from ccs.lcd import lcd


class NullLed:
    def stop(self):
        self.off()

    def set_color(self, color):
        pass

    def off(self):
        self.set_color(BLACK)


class NullLcd(lcd.Lcd):
    def __init__(self, serial_port, width=lcd.DEFAULT_WIDTH, height=lcd.DEFAULT_HEIGHT):
        self._width = width
        self._height = height

        self._ser = NullSerial()
        self._lines = [''] * height  # Screen starts blank
        self.set_size(width, height)
        self.clear()


class NullSerial:
    def write(self, data):
        pass

    def flush(self):
        pass

    def close(self):
        pass
