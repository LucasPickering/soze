from Adafruit_MotorHAT import Adafruit_MotorHAT

from .resource import SubscriberResource


class Led(SubscriberResource):

    _COLOR_LENGTH = 3  # RGB
    _COLOR_KEY = "reducer:led_color"

    def __init__(self, hat_addr, pins, *args, **kwargs):
        super().__init__(*args, sub_channel="r2d:led", **kwargs)

        if len(pins) != __class__._COLOR_LENGTH:
            raise ValueError(f"LED pins must be length 3 (RGB), got {pins}")
        self._pins = pins

        self._hat_addr = hat_addr
        self._hat = None

    @property
    def name(self):
        return "LED"

    def init(self):
        # Initialize the hat and each LED
        self._hat = Adafruit_MotorHAT(addr=self._hat_addr)
        for pin in self._pins:
            self._hat.getMotor(pin).run(Adafruit_MotorHAT.FORWARD)

    def cleanup(self):
        # Stop all PWM
        for pin in self._pins:
            self._hat.getMotor(pin).run(Adafruit_MotorHAT.RELEASE)

    def _read_data(self):
        data = self._redis.get(__class__._COLOR_KEY)
        if len(data) != __class__._COLOR_LENGTH:
            raise ValueError(
                f"Input data must be {__class__._COLOR_LENGTH} bytes (RGB),"
                f" got {len(data)} bytes"
            )
        return data

    def _on_pub(self, msg):
        data = self._read_data()
        # Color values are [0,255]. The HAT also expects values in this range,
        # but because of the way it is wired, 0 means full on and 255 means
        # full off. We need to invert the color values to correct for this.
        for pin, val in zip(self._pins, data):
            self._hat.getMotor(pin).setSpeed(255 - val)
