import socket
import time

from ccs import logger


def format_bytes(data):
    return ' '.join('{:02x}'.format(b) for b in data)


class SocketResource:
    def __init__(self, sock_addr, retry_time=3):
        # Open the socket
        self._sock_addr = sock_addr
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._retry_time = retry_time

    def open(self):
        while True:
            try:
                self._sock.connect(self._sock_addr)
                logger.debug(f"Connected to {self._sock_addr}")
                break  # Job's done
            except (FileNotFoundError, ConnectionRefusedError) as e:
                if self._retry_time is not None:
                    logger.error(f"Failed to connect to display socket {self._sock_addr} "
                                 f"Retrying in {self._retry_time} seconds...")
                    time.sleep(self._retry_time)  # Sleep for a bit, then try again
                else:
                    raise e  # Don't retry, just propagate the error

    def close(self):
        self._sock.close()

    def send(self, data):
        num_written = self._sock.send(data)
        if num_written != len(data):
            logger.error(f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                         f" but only sent {num_written} bytes")
        return num_written
