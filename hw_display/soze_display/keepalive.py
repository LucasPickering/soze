import RPi.GPIO as GPIO
import struct

from soze_core.resource import WriteResource


class Keepalive(WriteResource):
    def __init__(self, pin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pin = pin

    @property
    def name(self):
        return "Keepalive"

    def _init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)

    def _cleanup(self):
        GPIO.cleanup(self._pin)

    def _update(self):
        val = GPIO.input(self._pin)
        self._write(struct.pack("?", val))
