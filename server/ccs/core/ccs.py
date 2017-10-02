import argparse
import importlib
import logging
import os
import threading
import time
from collections import namedtuple

from . import api, color, settings
from .config import Config
from ccs import logger

HardwareData = namedtuple('HardwareData', 'led_color lcd_color lcd_text')


class CaseControlServer:
    _LED_THREAD_PAUSE = 0.1
    _LCD_THREAD_PAUSE = 0.1
    _HW_DATA_THREAD_PAUSE = 0.05

    def __init__(self, args):
        self._run = True
        self._debug = args.debug

        if self._debug:
            logger.setLevel(logging.DEBUG)

        # Init config and settings
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)
        config = Config(args.working_dir)
        settings.init(args.working_dir)

        self._hw_data = HardwareData(color.BLACK, color.BLACK, '')

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
        from ccs.led.led import Led
        from ccs.lcd.lcd import Lcd
        led_cfg = config['led']
        lcd_cfg = config['lcd']
        led = Led(led_cfg['red_pin'], led_cfg['green_pin'], led_cfg['blue_pin'])
        lcd = Lcd(lcd_cfg['device'], int(lcd_cfg['width']), int(lcd_cfg['height']))

        # Add background threads to be run
        def add_thread(target, **kwargs):
            thread = threading.Thread(target=target, **kwargs)
            self._threads.append(thread)
        self._threads = []
        add_thread(self._led_thread, name='LED-Thread', args=(led,))
        add_thread(self._lcd_thread, name='LCD-Thread', args=(lcd,))
        add_thread(self._hw_data_thread, name='HW-Data-Thread', daemon=True)

    def run(self):
        # Start the helper threads, then launch the REST API
        for thread in self._threads:
            thread.start()
        try:
            api.app.run(host='0.0.0.0')
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

    def _led_thread(self, led):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.
        """
        try:
            while self._run:
                led.set_color(self._hw_data.led_color)
                time.sleep(CaseControlServer._LED_THREAD_PAUSE)
            logger.debug("LED thread stopped")
        finally:
            led.stop()

    def _lcd_thread(self, lcd):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.
        """
        try:
            while self._run:
                lcd.set_color(self._hw_data.lcd_color)
                lcd.set_text(self._hw_data.lcd_text)
                time.sleep(CaseControlServer._LCD_THREAD_PAUSE)
            logger.debug("LCD thread stopped")
        finally:
            lcd.stop()

    def _hw_data_thread(self):
        """
        @brief      A thread that periodically re-calculates the hardware values from the settings.
        """
        while self._run:
            # Get LED color
            led_mode = settings.get('led.mode')
            led_color = led_mode.get_color(settings)

            # Get LCD color/text
            lcd_mode = settings.get('lcd.mode')
            use_led_color = settings.get('lcd.link_to_led')  # Use LED color for LCD
            lcd_color = led_color if use_led_color else lcd_mode.get_color(settings)
            lcd_text = lcd_mode.get_text(settings)

            # Update stuff then sleep
            self._hw_data = HardwareData(led_color, lcd_color, lcd_text)
            time.sleep(CaseControlServer._HW_DATA_THREAD_PAUSE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('working_dir', nargs='?', default='.',
                        help="Directory to store settings, config, etc.")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    parser.add_argument('--mock', '-m', action='store_const', default=False, const=True,
                        help="Mock the LEDs/LCD in the console for development")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()
