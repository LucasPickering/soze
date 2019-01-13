import logging

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
                "filename": "Adafruit_MotorHAT.log",
                "mode": "w",
            }
        },
        "loggers": {__name__: {"handlers": ["file"], "level": "DEBUG"}},
    }
)


class Adafruit_MotorHAT:

    FORWARD = "FORWARD"
    RELEASE = "RELEASE"

    def __init__(self, addr):
        self._addr = addr
        self._motors = {i: Motor(i) for i in range(1, 5)}
        logging.info(f"Set addr to {addr}")

    def getMotor(self, pin):
        return self._motors[pin]


class Motor:
    def __init__(self, pin):
        self._pin = pin

    def run(self, direction):
        logging.info(f"[{self._pin}] Direction: {direction}")

    def setSpeed(self, speed):
        logging.debug(f"[{self._pin}] Speed: {speed}")
