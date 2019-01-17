from mock_core import make_logger


logger = make_logger("GPIO")

BCM = "BCM"
IN = "IN"


def input(pin):
    logger.info(f"Read pin {pin}")
    return 1


def setmode(mode):
    logger.info(f"Set pin mode to {mode}")


def setup(pin, direction):
    logger.info(f"Set pin {pin} to {direction}")


def cleanup(pin):
    logger.info(f"Clean up pin {pin}")
