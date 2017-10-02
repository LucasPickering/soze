import abc
import socket

from ccs import logger


PWM_SOCKET = '/tmp/ccs_pwm_{pin}.sock'
LCD_SOCKET = '/tmp/ccs_lcd.sock'


class MockServer(metaclass=abc.ABCMeta):
    def __init__(self, sock_addr):
        self._addr = sock_addr
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._conn = None

    def start(self):
        self._sock.connect(self._addr)
        logger.info(f"Connected to {self._addr}")

    def write(self, data):
        self._sock.sendall(data)

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass
