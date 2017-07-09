#!/usr/bin/env python3

import argparse
import logging
import settings
import rest
import threading
import time
from lcd import Lcd
from led import Led


class Main:

    LED_THREAD_PAUSE = 0.01
    LCD_THREAD_PAUSE = 0.01
    SETTINGS_THREAD_PAUSE = 0.05

    def __init__(self, args):
        self.keep_running = True
        self.debug = args.debug
        self.init_logging(args.log)

        self.config = settings.Config(self.logger, args.config)
        self.user_settings = settings.UserSettings(self.logger, self.config)
        self.derived_settings = settings.DerivedSettings(self.logger, self.user_settings)

        # Init the case LED handler
        self.led = Led()

        # This thread constantly reads the derived settings and updates the LEDs accordingly
        self.led_thread = threading.Thread(target=self.led_thread)

        # Init the LCD handler
        self.lcd = Lcd(self.config.lcd_serial_device, self.config.lcd_width,
                       self.config.lcd_height)
        self.lcd.set_autoscroll(False)
        self.lcd.on()
        self.lcd.clear()

        # This thread constantly reads the derived settings and updates the LCD accordingly
        self.lcd_thread = threading.Thread(target=self.lcd_thread)

        # This thread constantly re-computes the derived settings from the user settings
        self.settings_thread = threading.Thread(target=self.settings_thread, daemon=True)

    def init_logging(self, log_file):
        # Init logging
        self.logger = logging.getLogger('case-control')
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)

        # Logging file handler
        fh = logging.FileHandler(log_file, mode='w')
        fh.setLevel(logging.DEBUG)

        # Logging console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if self.debug else logging.WARNING)

        # Setup formatter
        formatter = logging.Formatter('{asctime} - {levelname} - {message}',
                                      datefmt='%Y-%m-%d %H:%M:%S', style='{')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Register handlers
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def run(self):
        # Start the helper threads, then launch the REST API
        self.led_thread.start()
        self.lcd_thread.start()
        self.settings_thread.start()
        try:
            rest.run(self.user_settings, debug=self.debug)
        finally:
            # When flask receives Ctrl-C and stops, this runs to shut down the other threads
            self.stop()

    def stop(self):
        self.keep_running = False
        self.led_thread.join()
        self.lcd_thread.join()

    def led_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        while self.keep_running:
            color = self.derived_settings.led_color
            self.led.set_color(color.red, color.green, color.blue)
            time.sleep(self.LED_THREAD_PAUSE)
        self.led.stop()

    def lcd_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        while self.keep_running:
            self.lcd.set_color(self.derived_settings.lcd_color)
            self.lcd.set_text(self.derived_settings.lcd_text)
            time.sleep(self.LCD_THREAD_PAUSE)
        self.lcd.stop()

    def settings_thread(self):
        """
        @brief      A thread that periodically re-calculates the derived settings. These settings
                    are calculated from the user settings.

        @param      self  The object

        @return     None
        """
        while self.keep_running:
            self.derived_settings.update()
            time.sleep(self.SETTINGS_THREAD_PAUSE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('-c', '--config', default='config.ini', help="Specify the config file")
    parser.add_argument('-l', '--log', default='out.log', help="Specify the log file")
    args = parser.parse_args()

    main = Main(args)
    main.run()


if __name__ == '__main__':
    main()
