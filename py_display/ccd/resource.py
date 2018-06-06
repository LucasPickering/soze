import abc
import os
import socket
import traceback
from threading import Thread

from . import logger


def format_bytes(data):
    return ' '.join('{:02x}'.format(b) for b in data)


class Resource(metaclass=abc.ABCMeta):
    def __init__(self, name, socket):
        self._sock = None
        self._conn = None

        self._addr = socket
        self._thread = Thread(target=self._loop, name='{}-Thread'.format(name), daemon=True)
        self._run = True

    @property
    def is_open(self):
        return bool(self._sock and self._conn)

    def _open(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(self._addr)
        self._sock.listen(1)

        self._conn, addr = self._sock.accept()
        self._sock.settimeout(1.0)  # We want a timeout for read, but not accept
        logger.info(f"Connection on {self._addr}")

    def _read(self):
        return self._conn.recv(64)

    def _send(self, data):
        num_written = self._conn.send(data)
        if num_written != len(data):
            logger.error(f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                         f" but only sent {num_written} bytes")
        return num_written

    def _close_socket(self):
        self._conn = None
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()
        self._sock = None

    @abc.abstractmethod
    def _process_data(self, data):
        pass

    def _loop(self):
        try:
            while self._run:
                if self.is_open:
                    try:
                        data = self._read()
                        self._process_data(data)
                    except socket.timeout:
                        continue  # Read timeout, loop back again
                    except (ConnectionResetError, OSError) as e:
                        self._close_socket()
                else:
                    self._open()
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            self.close()

    def start(self):
        """
        @brief      Starts this resource. Opens up the socket and starts a thread that runs the
                    socket loop.
        """
        self._thread.start()

    def stop(self):
        """
        @brief      Stop the socket loop. When the loop stops, the resource will be closed.
        """
        self._run = False

    def close(self):
        """
        @brief      Close the resource. This will close the socket and any other associated I/O
                    resources, such as serial, I2C, etc. This does NOT stop the socket loop. You
                    probably don't want to call this - try Resource.stop instead.
        """
        try:
            self._close_socket()
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            if os.path.exists(self._addr):
                os.unlink(self._addr)
                logger.info(f"Closed {self._addr}")
