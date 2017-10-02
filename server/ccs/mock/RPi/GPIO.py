import struct

from ccs.mock.mock_server import MockServer, PWM_SOCKET

# Mocked GPIO constants
BOARD = None
OUT = None


class PWM(MockServer):
    def __init__(self, pin, *args, **kwargs):
        super().__init__(PWM_SOCKET.format(pin=pin))

    def start(self, dc):
        super().start()
        self.ChangeDutyCycle(dc)

    def ChangeDutyCycle(self, dc):  # Which idiot chose Pascal casing for Python???
        data = struct.pack('f', dc)
        super().write(data)

    def stop(self):
        super().close()

# Mocked GPIO methods


def setmode(pin_mode):
    pass


def setwarnings(on):
    pass


def setup(pin, mode):
    pass


def cleanup():
    pass
