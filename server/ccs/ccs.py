import argparse
import importlib
import logging
import os
import subprocess
import threading
import time
from collections import namedtuple

from ccs import app, logger
from .core import api, settings # Import api just to initialize it
from .core.color import BLACK
from .led.led_mode import LedMode
from .lcd.lcd_mode import LcdMode
from .lcd.helper import DEFAULT_WIDTH, DEFAULT_HEIGHT

HardwareData = namedtuple('HardwareData', 'led_color lcd_color lcd_text')


class CaseControlServer:
    _LED_THREAD_PAUSE = 0.1
    _LCD_THREAD_PAUSE = 0.1
    _HW_DATA_THREAD_PAUSE = 0.05
    _PING_THREAD_PAUSE = 1.0

    def __init__(self, args):
        self._run = True
        self._keepalive_up = True
        self._debug = args.debug

        if self._debug:
            logger.setLevel(logging.DEBUG)

        # Init settings
        if not os.path.exists(args.settings):
            os.makedirs(args.settings)
        settings.init(args.settings)

        self._hw_data = HardwareData(BLACK, BLACK, '')  # The values that get written to hardware

        # Mock hardware communication (PWM and serial)
        if args.mock:
            # Swap out some libraries with out mocked versions
            # Fake imports, SAD!!
            logger.info("Running in mocking mode")
            import sys
            sys.modules['RPi'] = importlib.import_module('ccs.mock.RPi')
            sys.modules['serial'] = importlib.import_module('ccs.mock.serial')

        # Init the LED/LCD handlers
        # Wait to import these in case their libraries are being mocked
        from .led.led import Led
        from .lcd.lcd import Lcd
        self._led = Led()
        self._lcd = Lcd(args.lcd_serial, args.lcd_width, args.lcd_height)

        # Add background threads to be run
        def add_thread(target, **kwargs):
            thread = threading.Thread(target=target, **kwargs)
            self._threads.append(thread)
        self._threads = []
        add_thread(self._led_thread, name='LED-Thread')
        add_thread(self._lcd_thread, name='LCD-Thread')
        add_thread(self._hw_data_thread, name='HW-Data-Thread', daemon=True)
        add_thread(self._ping_thread, name='Ping-Thread', args=[args.keepalive], daemon=True)

    def run(self):
        # Start the helper threads, then launch the REST API
        for thread in self._threads:
            thread.start()
        try:
            app.run(host='0.0.0.0')
        finally:
            # When flask receives Ctrl-C and stops, this runs to shut down the other threads
            self._stop()

    def _stop(self):
        logger.info("Stopping...")
        self._run = False

        # Wait for all blocking (i.e. non-daemon) threads to terminate
        logger.debug("Waiting for threads to stop...")
        for thread in self._threads:
            if not thread.daemon:
                thread.join()

    def _led_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.
        """
        try:
            while self._run:
                self._led.set_color(self._hw_data.led_color)
                time.sleep(CaseControlServer._LED_THREAD_PAUSE)
            logger.debug("LED thread stopped")
        finally:
            self._led.stop()

    def _lcd_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.
        """
        try:
            while self._run:
                self._lcd.set_color(self._hw_data.lcd_color)
                self._lcd.set_text(self._hw_data.lcd_text)
                time.sleep(CaseControlServer._LCD_THREAD_PAUSE)
            logger.debug("LCD thread stopped")
        finally:
            self._lcd.stop()

    def _hw_data_thread(self):
        """
        @brief      A thread that periodically re-calculates the hardware data from the settings.
        """
        while self._run:
            # Compute new values and store them
            if self._keepalive_up:
                led_color = LedMode.get_color(settings)
                lcd_color, lcd_text = LcdMode.get_color_and_text(self._lcd, settings)
            else:
                led_color = BLACK
                lcd_color, lcd_text = BLACK, ''
            self._hw_data = HardwareData(led_color, lcd_color, lcd_text)
            time.sleep(CaseControlServer._HW_DATA_THREAD_PAUSE)

    def _ping_thread(self, keepalive_host):
        """
        @brief      A thread that periodically pings the keepalive host. If the host doesn't repond,
                    the LED and LCD are shut off. If there is no host set, it is assumed to be up.
        """
        while self._run:
            success = True  # Assume true until we have a failing ping
            if keepalive_host:  # If a host was specified...
                exit_code = subprocess.call(['ping', '-c', '1', keepalive_host],
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                success = not exit_code

            # If the value changed, log it
            if success != self._keepalive_up:
                logger.debug(f"Keepalive up: {success}")
            self._keepalive_up = success

            time.sleep(CaseControlServer._PING_THREAD_PAUSE)  # Until we meet again...


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    parser.add_argument('--lcd-serial', default='/dev/ttyAMA0', help="Serial device for the LCD")
    parser.add_argument('--lcd-width', type=int, default=DEFAULT_WIDTH,
                        help="LCD width, in characters")
    parser.add_argument('--lcd-height', type=int, default=DEFAULT_HEIGHT,
                        help="LCD height, in characters")
    parser.add_argument('--keepalive', default=None, help="Host to use for keepalive check")
    parser.add_argument('--mock', '-m', action='store_const', default=False, const=True,
                        help="Mock the LEDs/LCD in the console for development")
    parser.add_argument('--settings', '-s', default='.',
                        help="Directory to store settings, config, etc.")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()
