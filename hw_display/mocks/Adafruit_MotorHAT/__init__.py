from mock_core import make_logger

logger = make_logger("Adafruit_MotorHAT")


class Adafruit_MotorHAT:

    FORWARD = "FORWARD"
    RELEASE = "RELEASE"

    def __init__(self, addr):
        self._addr = addr
        self._motors = {i: Motor(i) for i in range(1, 5)}
        logger.info(f"Set addr to {addr}")

    def getMotor(self, pin):
        return self._motors[pin]


class Motor:
    def __init__(self, pin):
        self._pin = pin

    def run(self, direction):
        logger.info(f"[{self._pin}] Direction: {direction}")

    def setSpeed(self, speed):
        logger.debug(f"[{self._pin}] Speed: {speed}")
