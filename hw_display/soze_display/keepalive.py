import RPi.GPIO as GPIO
import struct
import time
from threading import Event, Thread

from . import logger
from .resource import Resource


class Keepalive(Resource):

    _KEEPALIVE_KEY = "reducer:keepalive"
    _KEEPALIVE_CHANNEL = "r2d:keepalive"

    def __init__(self, *args, pin, **kwargs):
        super().__init__(*args, **kwargs)
        self._pin = pin
        self._thread = Thread(name="Keepalive", target=self._run)
        self._shutdown = Event()

    def _read_val(self):
        val = GPIO.input(self._pin)
        return struct.pack("?", val)

    @property
    def should_run(self):
        return not self._shutdown.is_set()

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)

    def cleanup(self):
        GPIO.cleanup(self._pin)

    def start(self):
        self._thread.start()

    def stop(self):
        self._shutdown.set()

    def _run(self):
        logger.info("Keepalive started")
        while self.should_run:
            # Update
            self._redis.set(__class__._KEEPALIVE_KEY, self._read_val())
            self._redis.publish(__class__._KEEPALIVE_CHANNEL, b"")
            time.sleep(1)
        logger.info("Keepalive stopped")
