import logging

BCM = "BCM"
IN = "IN"


def input(pin):
    logging.info(f"Read pin {pin}")
    return 1


def setmode(mode):
    logging.info(f"Set pin mode to {mode}")


def setup(pin, direction):
    logging.info(f"Set pin {pin} to {direction}")


def cleanup(pin):
    logging.info(f"Clean up pin {pin}")
