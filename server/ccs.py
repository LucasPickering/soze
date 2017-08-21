#!/usr/bin/env python3

import argparse
import logging
import settings
import subprocess
import threading
import time
from flask import Flask, json, request

from lcd import Lcd
from led import Led
from color import Color

BLACK = Color(0, 0, 0)

app = Flask(__name__)
user_settings = None  # Will be initialized in Main constructor


def to_json(data):
    if 'pretty' in request.args:
        return json.dumps(data, indent=4) + '\n'
    return json.dumps(data)


@app.route('/')
def root():
    return to_json(user_settings.to_dict())


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic'


@app.route('/led', methods=['GET', 'POST'])
def led():
    if request.method == 'GET':
        return to_json(user_settings.to_dict()['led'])
    elif request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_led_mode(data['mode'])
        if 'static_color' in data:
            user_settings.set_led_static_color(data['static_color'])
        return "Success"


@app.route('/led/fade', methods=['GET', 'POST'])
def led_fade():
    if request.method == 'GET':
        return to_json(user_settings.to_dict()['led']['fade'])
    elif request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_led_mode(data['mode'])
        if 'static_color' in data:
            user_settings.set_led_static_color(data['static_color'])
        return "Success"


@app.route('/lcd', methods=['GET', 'POST'])
def lcd():
    if request.method == 'GET':
        return to_json(user_settings.to_dict()['lcd'])
    elif request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_lcd_mode(data['mode'])
        if 'color' in data:
            user_settings.set_lcd_color(data['color'])
        return "Success"


class Main:

    LED_THREAD_PAUSE = 0.01
    LCD_THREAD_PAUSE = 0.01
    SETTINGS_THREAD_PAUSE = 0.05
    PING_THREAD_PAUSE = 1.0

    def __init__(self, args):
        self.keep_running = True
        self.keepalive_up = True
        self.debug = args.debug
        self.init_logging(args.log)

        self.config = settings.Config(self.logger, args.config)
        self.user_settings = settings.UserSettings(args.settings, self.logger, self.config)
        self.derived_settings = settings.DerivedSettings(self.logger, self.user_settings)

        global user_settings  # GLOBALS ARE GREAT
        user_settings = self.user_settings

        # Init the case LED handler
        self.led = Led()

        # This thread constantly reads the derived settings and updates the LEDs accordingly
        self.led_thrd = threading.Thread(target=self.led_thread)

        # Init the LCD handler
        self.lcd = Lcd(self.config.lcd_serial_device, self.config.lcd_width,
                       self.config.lcd_height)
        self.lcd.set_autoscroll(False)
        self.lcd.on()
        self.lcd.clear()

        # This thread constantly reads the derived settings and updates the LCD accordingly
        self.lcd_thrd = threading.Thread(target=self.lcd_thread)

        # This thread constantly re-computes the derived settings from the user settings
        self.settings_thrd = threading.Thread(target=self.settings_thread, daemon=True)

        self.ping_thrd = threading.Thread(target=self.ping_thread, daemon=True)

    def init_logging(self, log_file):
        # Init logging
        self.logger = app.logger
        self.logger.setLevel(logging.DEBUG)

        # Logging file handler
        fh = logging.FileHandler(log_file, mode='w')
        fh.setLevel(logging.DEBUG if self.debug else logging.INFO)

        # Logging console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if self.debug else logging.INFO)

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
        self.led_thrd.start()
        self.lcd_thrd.start()
        self.settings_thrd.start()
        self.ping_thrd.start()
        try:
            # app.run(debug=self.debug, host='0.0.0.0')
            app.run(host='0.0.0.0')
        finally:
            # When flask receives Ctrl-C and stops, this runs to shut down the other threads
            self.stop()

    def stop(self):
        self.logger.info("Stopping...")
        self.keep_running = False
        self.led_thrd.join()
        self.lcd_thrd.join()

    def led_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        try:
            while self.keep_running:
                color = self.derived_settings.led_color if self.keepalive_up else BLACK
                self.led.set_color(color.red, color.green, color.blue)
                time.sleep(self.LED_THREAD_PAUSE)
        except Exception as e:
            self.logger.error(e)
        self.led.stop()
        self.logger.info("LED thread stopped")

    def lcd_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        while self.keep_running:
            if self.keepalive_up:
                color = self.derived_settings.lcd_color
                text = self.derived_settings.lcd_text
            else:
                color = BLACK
                text = ''
            self.lcd.set_color(color)
            self.lcd.set_text(text)
            # self.lcd.flush_serial()  # Maybe uncomment this if we have problems?`
        self.lcd.off()
        self.lcd.clear()
        self.lcd.stop()
        self.logger.info("LCD thread stopped")

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

    def ping_thread(self):
        """
        @brief      A thread that periodically pings the keepalive host. If the host doesn't repond,
                    the LED and LCD are shut off. If there is no host set, it is assumed to be up.

        @param      self  The object

        @return     None
        """
        while self.keep_running:
            time.sleep(self.PING_THREAD_PAUSE)
            if self.config.keepalive_host:
                exit_code = subprocess.call(['ping', '-c', '1', self.config.keepalive_host],
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if exit_code:
                    if self.keepalive_up:
                        self.logger.debug("Keepalive down")
                    self.keepalive_up = False
                    continue
            if not self.keepalive_up:
                self.logger.log(logging.DEBUG, "Keepalive up")
            self.keepalive_up = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('-c', '--config', default='config.ini', help="Specify the config file")
    parser.add_argument('-l', '--log', default='out.log', help="Specify the log file")
    parser.add_argument('-s', '--settings', default='settings.json',
                        help="Specify the settings file that will be saved to and loaded from")
    args = parser.parse_args()

    main = Main(args)
    main.run()


if __name__ == '__main__':
    main()
