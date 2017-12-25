import abc
import os
import socket
import traceback
from threading import Thread

from . import logger


def format_bytes(data):
    return ' '.join('{:02x}'.format(b) for b in data)


class Resource(metaclass=abc.ABCMeta):
    def __init__(self, name, sock_addr):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._addr = sock_addr
        self._thread = Thread(target=self._loop, name='{}-Thread'.format(name), daemon=True)
        self._run = True

    def _read_data(self):
        return self._sock.recv(64)

    @abc.abstractmethod
    def _process_data(self, data):
        pass

    def _loop(self):
        try:
            while self._run:
                data = self._read_data()
                logger.debug(format_bytes(data))
                self._process_data(data)
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            self.close()

    def start(self):
        self._sock.bind(self._addr)
        self._thread.start()

    def close(self):
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            logger.info(f"Closed {self}")
        except Exception:
            pass
        finally:
            if os.path.exists(self._addr):
                os.unlink(self._addr)

    def __str__(self):
        return self._addr
