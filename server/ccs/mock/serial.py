import socket

from ccs.lcd.helper import LCD_MOCK_SOCKET

# Mocked serial constants
EIGHTBITS = None
PARITY_NONE = None
STOPBITS_ONE = None


class Serial:
    def __init__(self, *args, **kwargs):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.connect(LCD_MOCK_SOCKET)
        self.total_bytes = 0

    def write(self, data):
        num_bytes = len(data)
        self.total_bytes += num_bytes
        print(f"Sending {num_bytes} bytes; {self.total_bytes} total bytes")
        self._sock.sendall(data)

    def flush(self):
        pass

    def close(self):
        self._sock.close()
