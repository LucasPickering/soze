import argparse
import importlib
import logging
import os
import time
from multiprocessing import Process
from threading import Thread

from . import api, settings
from .config import Config
from ccs import logger


class CaseControlServer:
    _LED_THREAD_PAUSE = 0.1
    _LCD_THREAD_PAUSE = 0.1

    def __init__(self, args):
        self._run = True

        if args.debug:
            logger.setLevel(logging.DEBUG)

        # Init config and settings
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)
        config = Config(args.working_dir)
        settings.init(args.working_dir)

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
        led = Led(int(led_cfg['red_pin']), int(led_cfg['green_pin']), int(led_cfg['blue_pin']))
        logger.debug("Initialized LED")
        lcd = Lcd(lcd_cfg['device'], int(lcd_cfg['width']), int(lcd_cfg['height']))
        logger.debug("Initialized LCD")

        # Add background threads/processes to be run
        self._api_proc = Process(target=api.app.run, kwargs={'host': '0.0.0.0'})
        self._threads = [
            Thread(target=self._led_thread, name='LED-Thread', args=(led,)),
            Thread(target=self._lcd_thread, name='LCD-Thread', args=(lcd,)),
        ]

    def run(self):
        # Start the helper threads, then launch the REST API
        try:
            logger.debug("Starting threads...")
            for thread in self._threads:
                thread.start()
            logger.debug("Started threads, now starting Flask...")
            self._api_proc.start()
            logger.debug("Started Flask")

            self._wait()  # Wait for something to die
        except KeyboardInterrupt:
            pass
        finally:
            self._stop()  # Shut down every thread/process

    def _wait(self):
        for thread in self._threads:
            thread.join()
        self._api_proc.join()

    def _stop(self):
        # Stop, if this hasn't already been called once
        if self._run:
            logger.info("Stopping...")
            self._run = False
            self._api_proc.terminate()

    def _led_thread(self, led):
        """
        @brief      A thread that periodically updates the case LEDs based on the current settings.
        """
        try:
            while self._run:
                led_mode = settings.get('led.mode')
                led.set_color(led_mode.get_color(settings))
                time.sleep(CaseControlServer._LED_THREAD_PAUSE)
            logger.debug("LED thread stopped")
        finally:
            self._stop()
            led.stop()

    def _lcd_thread(self, lcd):
        """
        @brief      A thread that periodically updates the case LEDs based on the current settings.
        """
        try:
            while self._run:
                mode = settings.get('lcd.mode')
                text = mode.get_text(settings)
                if settings.get('lcd.link_to_led'):  # Special setting to use LED color for LCD
                    mode = settings.get('led.mode')
                color = mode.get_color(settings)

                lcd.set_text(text)
                lcd.set_color(color)
                time.sleep(CaseControlServer._LCD_THREAD_PAUSE)
            logger.debug("LCD thread stopped")
        finally:
            self._stop()
            lcd.stop()


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
