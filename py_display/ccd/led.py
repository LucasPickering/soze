import RPi.GPIO as GPIO
import traceback

from . import logger
from .resource import Resource


class PwmPin:

    PWM_FREQ = 100  # Frequency of PWM wave, in Hz

    def __init__(self, pin_num):
        GPIO.setup(pin_num, GPIO.OUT)
        self._pwm = GPIO.PWM(pin_num, PwmPin.PWM_FREQ)
        self._pwm.start(0)

    def set_color(self, color_val):
        duty_cycle = color_val / 255.0 * 100  # Convert color val [0, 255] to duty cycle [0, 100]
        self._pwm.ChangeDutyCycle(duty_cycle)

    def stop(self):
        self._pwm.stop()


class Led(Resource):
    def __init__(self, sock_addr, red_pin, green_pin, blue_pin):
        super().__init__('LED', sock_addr)

        # Init pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        # Init and start a PWM controller for each pin
        self._red_pwm = PwmPin(red_pin)
        self._green_pwm = PwmPin(green_pin)
        self._blue_pwm = PwmPin(blue_pin)

    def _process_data(self, data):
        # Unpack colors from data
        red, green, blue = data
        self._red_pwm.set_color(red)
        self._green_pwm.set_color(green)
        self._blue_pwm.set_color(blue)

    def stop(self):
        super().stop()
        try:
            self.off()
        except Exception:
            logger.error("Error turning off LEDs:\n{}".format(traceback.format_exc()))
        finally:
            self._red_pwm.stop()
            self._green_pwm.stop()
            self._blue_pwm.stop()
            GPIO.cleanup()
