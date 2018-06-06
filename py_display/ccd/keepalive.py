import RPi.GPIO as GPIO
import struct

from .resource import Resource


class Keepalive(Resource):

    def __init__(self, pin, *args, **kwargs):
        super().__init__('Keepalive', *args, **kwargs)
        self._pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)

    def _process_data(self, data):
        val = GPIO.input(self._pin)
        self._send(struct.pack('?', val))

    def close(self):
        super().close()
        GPIO.cleanup(self._pin)
