import RPi.GPIO as GPIO
import struct

from cc_core.resource import WriteResource


class Keepalive(WriteResource):

    def __init__(self, pin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pin = pin

    @property
    def name(self):
        return 'Keepalive'

    def _open(self):
        if super()._open():
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.IN)
            return True
        return False

    def _close(self):
        GPIO.cleanup(self._pin)
        return super()._close()

    def _update(self):
        val = GPIO.input(self._pin)
        self._write(struct.pack('?', val))
