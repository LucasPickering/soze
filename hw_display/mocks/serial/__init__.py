from mock_core import format_bytes, make_logger

EIGHTBITS = 8
PARITY_NONE = 0
STOPBITS_ONE = 1

logger = make_logger("serial")


def _format_bytes(data):
    return " ".join("{:02x}".format(b) for b in data)


class Serial:
    def __init__(self, baudrate, bytesize, parity, stopbits):
        self._port = None

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    def open(self):
        if self.port is None:
            raise ValueError("No port assigned")
        logger.info(f"{self.port} opened")

    def close(self):
        logger.info(f"{self.port} closed")

    def flush(self):
        logger.info(f"{self.port} flushed")

    def write(self, data):
        logger.debug(format_bytes(data))
        return len(data)
