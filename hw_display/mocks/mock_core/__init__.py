import logging.config

EIGHTBITS = 8
PARITY_NONE = 0
STOPBITS_ONE = 1

f = logging.Formatter(
    fmt="{asctime} [{levelname:>7}] {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)


def make_logger(name):
    fh = logging.FileHandler(f"mock_logs/{name}.log", mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(f)

    logger = logging.getLogger(name)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    return logger


def format_bytes(data):
    return " ".join("{:02x}".format(b) for b in data)
