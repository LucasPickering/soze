from .mock_server import MockServer
from ccs.lcd.helper import LCD_MOCK_SOCKET

# Mocked serial constants
EIGHTBITS = None
PARITY_NONE = None
STOPBITS_ONE = None


class Serial(MockServer):
    def __init__(self, *args, **kwargs):
        super().__init__(LCD_MOCK_SOCKET)
        self.start()

    def write(self, data):
        super().write(data)
        pass

    def flush(self):
        pass

    def close(self):
        super().stop()
