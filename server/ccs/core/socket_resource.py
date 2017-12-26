import abc
import socket
import time
from threading import Thread

from ccs import logger

THREAD_PAUSE = 0.1  # Time between iterations of the main loop
RETRY_PAUSE = 3  # Time to wait after a failed socket connect before trying again


def format_bytes(data):
    return ' '.join('{:02x}'.format(b) for b in data)


class SocketResource(metaclass=abc.ABCMeta):
    def __init__(self, sock_addr):
        # Open the socket
        self._sock_addr = sock_addr
        self._sock = None
        self._run = True
        self._awake = True

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    def awake(self):
        return self._awake

    @awake.setter
    def awake(self, awake):
        self._awake = awake

    @property
    def is_open(self):
        return bool(self._sock)

    def _open(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        while self._run:
            try:
                self._sock.connect(self._sock_addr)
                logger.debug(f"Connected to {self._sock_addr}")
                return True  # Job's done
            except (FileNotFoundError, ConnectionRefusedError) as e:
                logger.warning(f"Failed to connect to display socket {self._sock_addr}. "
                               f"Retrying in {RETRY_PAUSE} seconds...")
                time.sleep(RETRY_PAUSE)  # Sleep for a bit, then try again
        self._sock = None  # Reset the value of sock so we know init failed
        return False

    def _close(self):
        self._sock.close()
        self._sock = None
        logger.debug(f"Disconnected from {self._sock_addr}")

    def init(self):
        pass

    def cleanup(self):
        pass

    def send(self, data):
        num_written = self._sock.send(data)
        if num_written != len(data):
            logger.error(f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                         f" but only sent {num_written} bytes")
        return num_written

    @abc.abstractmethod
    def _get_default_values(self, settings):
        pass

    @abc.abstractmethod
    def _get_values(self, settings):
        pass

    @abc.abstractmethod
    def _apply_values(self, *values):
        pass

    def run_loop(self, settings):
        """
        @brief      A loop that periodically sends updates to the display for this resource.
        """
        try:
            while self._run:
                if self.is_open:
                    values = self._get_values(settings) if self.awake \
                        else self._get_default_values(settings)

                    try:
                        self._apply_values(*values)
                        time.sleep(THREAD_PAUSE)
                    except (ConnectionResetError, OSError):
                        self._close()  # Close the socket so we can try again
                else:
                    # No socket connection yet, open one now
                    if self._open():
                        self.init()
        finally:
            if self.is_open:
                self.cleanup()
                self._close()

    def make_thread(self, settings):
        return Thread(target=self.run_loop, name=f'{self.name}-Thread', args=(settings,))

    def stop_loop(self):
        self._run = False
