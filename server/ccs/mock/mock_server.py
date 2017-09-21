import abc
import socket
import time

from ccs import logger


class MockServer(metaclass=abc.ABCMeta):
    def __init__(self, sock_addr):
        self._addr = sock_addr
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._conn = None

    def start(self):
        self._sock.connect(self._addr)
        logger.info(f"Connected to {self._addr}")

    def write(self, data):
        while True:
            try:
                self._sock.sendall(data)
                break
            except OSError as e:
                if e.errno == 55:
                    logger.error(f"Buffer full on {self._addr}. Will retry...")
                    time.sleep(0.1)
                    # try again
                else:
                    raise

    def stop(self):
        try:
            self._sock.close()
        except OSError:
            pass
