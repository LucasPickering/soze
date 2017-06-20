#!/usr/bin/env python3

import argparse
import rest
import threading
import time
from lcd import Lcd
from led import Led
from model import Model


class Main:

    LED_THREAD_PAUSE = 0.05
    LCD_THREAD_PAUSE = 0.05

    def __init__(self, args):
        self.run = True
        self.debug = args.debug
        self.model = Model()

        # Init the case LED handler
        self.led = Led()
        self.led_thread = threading.Thread(target=self.led_thread)

        # Init the LCD handler
        self.lcd = Lcd(args.serial)
        self.lcd.set_autoscroll(False)
        self.lcd.on()
        self.lcd.clear()
        self.lcd_thread = threading.Thread(target=self.lcd_thread)

    def start(self):
        # Start the helper threads, then launch the REST API
        self.led_thread.start()
        self.lcd_thread.start()
        rest.run(self.model)

    def stop(self):
        self.run = False

    def led_thread(self):
        while self.run:
            color = self.model.led_color
            self.led.set_color(color.red, color.green, color.blue)
            time.sleep(self.LED_THREAD_PAUSE)

    def lcd_thread(self):
        while self.run:
            time.sleep(self.LCD_THREAD_PAUSE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--serial', default='/dev/ttyAMA0',
                        help="Serial port to communicate with the LCD on")
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    main = Main(args)
    main.start()


if __name__ == '__main__':
    main()
