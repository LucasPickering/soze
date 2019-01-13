import logging.config

EIGHTBITS = 8
PARITY_NONE = 0
STOPBITS_ONE = 1

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "f": {
                "format": "{asctime} [{levelname:<7}] {message}",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{",
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "formatter": "f",
                "filename": "pyserial.log",
                "mode": "w",
            }
        },
        "loggers": {__name__: {"handlers": ["file"], "level": "DEBUG"}},
    }
)


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
        logging.info(f"{self.port} opened")

    def close(self):
        logging.info(f"{self.port} closed")

    def flush(self):
        logging.info(f"{self.port} flushed")

    def write(self, data):
        logging.debug(_format_bytes(data))
        return len(data)
