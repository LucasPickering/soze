import argparse

from ccs import logger
from ccs.core.color import BLACK

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    logger.warning("RPi.GPIO library not installed")


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

    # Hardware pin numbers, please don't ask about the ordering that's just how I wired it
    RED_PIN = 5
    GREEN_PIN = 3
    BLUE_PIN = 7

    def __init__(self):
        # Init pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        # Init and start a PWM controller for each pin
        self._red_pwm = PwmPin(Led.RED_PIN)
        self._green_pwm = PwmPin(Led.GREEN_PIN)
        self._blue_pwm = PwmPin(Led.BLUE_PIN)

    def set_color(self, color):
        def to_duty_cycle(color_val):
            return color_val / 255.0 * 100
        self._red_pwm.set_color(color.red)
        self._green_pwm.set_color(color.green)
        self._blue_pwm.set_color(color.blue)

    def stop(self):
        self.off()
        self._red_pwm.stop()
        self._green_pwm.stop()
        self._blue_pwm.stop()
        GPIO.cleanup()

    def off(self):
        self.set_color(BLACK)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('red', type=int, help="Red value, [0, 255]")
    parser.add_argument('green', type=int, help="Green value, [0, 255]")
    parser.add_argument('blue', type=int, help="Blue value, [0, 255]")
    args = parser.parse_args()

    led = Led()
    led.set_color(args.red, args.green, args.blue)
    input('Press Enter to stop: ')
    led.stop()


if __name__ == '__main__':
    main()
