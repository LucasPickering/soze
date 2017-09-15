import abc
import os
import socket
import threading

from ccs import logger


class MockServer(metaclass=abc.ABCMeta):
    def __init__(self, sock_addr):
        self._addr = sock_addr
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._conn = None

    def start(self):
        self._sock.bind(self._addr)
        self._sock.listen(1)
        self._wait_for_client()

    def _wait_for_client(self):
        def accept():
            try:
                self._conn, _ = self._sock.accept()
                logger.info(f"Client connected to {self._addr}")
            except Exception:
                pass

        thread = threading.Thread(target=accept, daemon=True)
        thread.start()

    def write(self, data):
        if self._conn:
            try:
                self._conn.sendall(data)
            except socket.error:
                logger.info(f"Client disconnected from {self._addr}")
                self._close_conn()
                self._wait_for_client()

    def _close_conn(self):
        self._conn.close()
        self._conn = None

    def stop(self):
        if self._conn:
            self._close_conn()
        self._sock.close()
        self._sock = None

        try:
            os.unlink(self._addr)
        except FileNotFoundError:
            pass
