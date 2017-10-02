import RPi.GPIO as GPIO
import traceback

from ccs import logger
from ccs.core.color import BLACK


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


class Led:

    def __init__(self, red_pin, green_pin, blue_pin):
        # Init pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        # Init and start a PWM controller for each pin
        self._red_pwm = PwmPin(red_pin)
        self._green_pwm = PwmPin(green_pin)
        self._blue_pwm = PwmPin(blue_pin)

    def set_color(self, color):
        self._red_pwm.set_color(color.red)
        self._green_pwm.set_color(color.green)
        self._blue_pwm.set_color(color.blue)

    def stop(self):
        try:
            self.off()
        except Exception:
            logger.error("Error turning off LEDs:\n{}".format(traceback.format_exc()))
        finally:
            self._red_pwm.stop()
            self._green_pwm.stop()
            self._blue_pwm.stop()
            GPIO.cleanup()

    def off(self):
        self.set_color(BLACK)
