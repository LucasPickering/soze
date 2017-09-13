import socket
import struct

from ccs.led.helper import LED_PWM_SOCKET

# Mocked GPIO constants
BOARD = None
OUT = None


class PWM:
    def __init__(self, pin, *args, **kwargs):  # extra args to match the sig of GPIO.PWM
        self._addr = LED_PWM_SOCKET.format(pin=pin)
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    def start(self, dc):
        self._sock.connect(self._addr)
        self.ChangeDutyCycle(dc)

    def ChangeDutyCycle(self, dc):  # Which idiot chose Pascal casing for Python???
        data = struct.pack('f', dc)
        # self._sock.sendall(data)

    def stop(self):
        self._sock.close()


# Mocked GPIO methods


def setmode(pin_mode):
    pass


def setwarnings(on):
    pass


def setup(pin, mode):
    pass


def cleanup():
    pass
