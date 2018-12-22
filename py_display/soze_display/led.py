from Adafruit_MotorHAT import Adafruit_MotorHAT

from soze_core.resource import ReadResource


class Led(ReadResource):
    def __init__(self, hat_addr, pins, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if len(pins) != 3:
            raise ValueError(f"LED pins must be length 3 (RGB), got {pins}")
        self._pins = pins

        self._hat_addr = hat_addr
        self._hat = None

    @property
    def name(self):
        return "LED"

    def _init(self):
        # Initialize the hat and each LED
        self._hat = Adafruit_MotorHAT(addr=self._hat_addr)
        for pin in self._pins:
            self._hat.getMotor(pin).run(Adafruit_MotorHAT.FORWARD)

    def _cleanup(self):
        # Stop all PWM
        for pin in self._pins:
            self._hat.getMotor(pin).run(Adafruit_MotorHAT.RELEASE)

    def _process_data(self, data):
        if len(data) != 3:
            raise ValueError(f"Input data must be length 3 (RGB), got {data}")
        # Color values are [0,255]. The HAT also expects values in this range, but because of the
        # way it is wired, 0 means full on and 255 means full off. We need to invert the color
        # values to correct for this.
        for pin, val in zip(self._pins, data):
            self._hat.getMotor(pin).setSpeed(255 - val)
