#!/usr/bin/env python3

import argparse
import rest
import threading
import time
from lcd import Lcd
from led import Led
from model import Color, Settings


class Main:

    LED_THREAD_PAUSE = 0.01
    LCD_THREAD_PAUSE = 0.01

    def __init__(self, args):
        self.keep_running = True
        self.debug = args.debug
        self.settings = Settings(Color(255, 255, 0), Color(0, 0, 0), '')

        # Init the case LED handler
        self.led = Led()
        self.led_thread = threading.Thread(target=self.led_thread)

        # Init the LCD handler
        self.lcd = Lcd(args.serial)
        self.lcd.set_autoscroll(False)
        self.lcd.on()
        self.lcd.clear()
        self.lcd_thread = threading.Thread(target=self.lcd_thread)

    def run(self):
        # Start the helper threads, then launch the REST API
        self.led_thread.start()
        self.lcd_thread.start()
        try:
            rest.run(self.settings, debug=self.debug)
        finally:
            # When flask receives Ctrl-C and stops, this runs to shut down the other threads
            self.stop()

    def stop(self):
        self.keep_running = False
        self.led_thread.join()
        self.lcd_thread.join()

    def led_thread(self):
        while self.keep_running:
            color = self.settings.led_color
            self.led.set_color(color.red, color.green, color.blue)
            time.sleep(self.LED_THREAD_PAUSE)
        self.led.stop()

    def lcd_thread(self):
        while self.keep_running:
            # TODO
            time.sleep(self.LCD_THREAD_PAUSE)
        self.lcd.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--serial', default='/dev/ttyAMA0',
                        help="Serial port to communicate with the LCD on")
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    main = Main(args)
    main.run()


if __name__ == '__main__':
    main()
