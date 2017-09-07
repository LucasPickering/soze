from ccs.led.led import Led
from ccs.lcd.lcd import Lcd


class NullLed(Led):

    def __init__(self):
        pass

    def set_color(self, color):
        pass

    def stop(self):
        self.off()


class NullLcd(Lcd):

    def __init__(self, serial_port, width, height):
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
