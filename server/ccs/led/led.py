import argparse
import RPi.GPIO as GPIO


class Led:

    PWM_FREQ = 100  # Frequency of PWM wave, in Hz

    # Hardware pin numbers, please don't ask about the ordering that's just how I wired it
    RED_PIN = 5
    GREEN_PIN = 3
    BLUE_PIN = 7

    def __init__(self):
        # Init pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.RED_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_PIN, GPIO.OUT)
        GPIO.setup(self.BLUE_PIN, GPIO.OUT)

        # Init and start a PWM controller for each pin
        self.red_pwm = GPIO.PWM(self.RED_PIN, self.PWM_FREQ)
        self.green_pwm = GPIO.PWM(self.GREEN_PIN, self.PWM_FREQ)
        self.blue_pwm = GPIO.PWM(self.BLUE_PIN, self.PWM_FREQ)

        self.red_pwm.start(0)
        self.green_pwm.start(0)
        self.blue_pwm.start(0)

    def set_color(self, color):
        def to_duty_cycle(color_val):
            return color_val / 255.0 * 100
        self.red_pwm.ChangeDutyCycle(to_duty_cycle(color.red))
        self.green_pwm.ChangeDutyCycle(to_duty_cycle(color.green))
        self.blue_pwm.ChangeDutyCycle(to_duty_cycle(color.blue))

    def stop(self):
        self.off()
        self.red_pwm.stop()
        self.green_pwm.stop()
        self.blue_pwm.stop()
        GPIO.cleanup()

    def off(self):
        self.set_color(0, 0, 0)


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
