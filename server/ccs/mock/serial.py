from .mock_server import MockServer, LCD_SOCKET

# Mocked serial constants
EIGHTBITS = None
PARITY_NONE = None
STOPBITS_ONE = None


class Serial(MockServer):
    def __init__(self, *args, **kwargs):
        super().__init__(LCD_SOCKET)
        self.start()

    def write(self, data):
        super().write(data)
        return len(data)  # Let's just assume we wrote it all

    def flush(self):
        pass

    def close(self):
        super().stop()
