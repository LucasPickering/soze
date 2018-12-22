import abc
import os
import socket
import time
import traceback
from threading import Event, Thread

from . import logger


def format_bytes(data):
    return " ".join("{:02x}".format(b) for b in data)


class Resource(Thread, metaclass=abc.ABCMeta):

    OPEN_RETRY_PAUSE = 3.0

    def __init__(self, socket_addr, pause=0.1, **kwargs):
        super().__init__(name=f"{self.name}-Thread", target=self._loop)
        self._shutdown = Event()
        self._socket_addr = socket_addr
        # If the address is a string, then assume this is a Unix Domain Socket
        self._is_uds = isinstance(socket_addr, str)
        self._pause = pause
        self._init_socket()

    def _init_socket(self):
        self._socket = socket.socket(
            socket.AF_UNIX if self._is_uds else socket.AF_INET,
            socket.SOCK_DGRAM,
        )
        self._socket.settimeout(1.0)

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    def should_run(self):
        return not self._shutdown.is_set()

    @abc.abstractmethod
    def _open(self):
        pass

    def _close(self):
        self._socket.close()
        logger.info(f"Disconnected from {self._socket_addr}")

    def _init(self):
        """
        @brief      Runs before the main loop, and before any socket is opened.
                    This should be used for opening hardware resources.
        """
        pass

    def _cleanup(self):
        """
        @brief      Runs after the socket is shut down and the main loop exits.
                    This should be used to close hardware resources.
        """
        pass

    def _after_open(self):
        """
        @brief      Runs immediately after the socket is opened. Should be used
                    for initialization that requires the socket.
        """
        pass

    def _before_close(self):
        """
        @brief      Runs immediately before the socket closes, but only during
                    a graceful stop. If the socket is closing because of an
                    error, this will NOT be called. Should be used for cleanup
                    that requires the socket.
        """
        pass

    @abc.abstractmethod
    def _update(self):
        pass

    def _loop(self):
        try:
            self._init()
            while self.should_run:
                if self._open():
                    try:
                        self._after_open()
                        while self.should_run:
                            self._update()
                            time.sleep(self._pause)
                        self._before_close()
                    except (ConnectionRefusedError, socket.timeout):
                        pass
                    finally:
                        self._close()
                        # Re-create the socket so we can try again
                        self._init_socket()
                else:
                    logger.debug(
                        f"Failed to open socket {self._socket_addr}. "
                        f"Retrying in {self.OPEN_RETRY_PAUSE} seconds..."
                    )
                    time.sleep(
                        self.OPEN_RETRY_PAUSE
                    )  # Sleep for a bit, then try again
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            self._cleanup()

    def stop(self):
        if self.should_run:
            logger.info(f"Stopping {self.name}")
            self._shutdown.set()


class ReadResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, pause=0, **kwargs)

    def _open(self):
        try:
            self._socket.bind(self._socket_addr)
            logger.debug(f"Listening on {self._socket_addr}")
            return True
        except OSError as e:
            if e.errno == 98:
                # Address already in use. Only relevant for UDS.
                logger.warning(
                    f"{self._socket_addr} already exists, removing it..."
                )
                os.unlink(self._socket_addr)  # Remove the file and try again
                return False
            raise e

    def _close(self):
        super()._close()
        if self._is_uds:
            os.unlink(self._socket_addr)

    def _read(self, num_bytes=64):
        try:
            return self._socket.recv(num_bytes)
        except socket.timeout:
            return None

    @abc.abstractmethod
    def _process_data(self, data):
        pass

    def _update(self):
        data = self._read()
        if data:
            self._process_data(data)


class WriteResource(Resource):
    def _open(self):
        try:
            self._socket.connect(self._socket_addr)
            logger.info(f"Connected to {self._socket_addr}")
            return True  # Job's done
        except (FileNotFoundError, ConnectionRefusedError) as e:
            return False

    def _write(self, data):
        num_written = self._socket.send(data)
        if num_written != len(data):
            logger.error(
                f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                f" but only sent {num_written} bytes"
            )
        return num_written
