import logging
import subprocess
import threading
import time
from collections import namedtuple

from ccs import app, logger
from .core.config import Config
from .core.settings import Settings
from .core.color import BLACK
from .lcd import lcd_mode
from .led import led_mode

HardwareData = namedtuple('HardwareData', 'led_color lcd_color lcd_text')

_LED_THREAD_PAUSE = 0.01
_LCD_THREAD_PAUSE = 0.01
_HW_DATA_THREAD_PAUSE = 0.05
_PING_THREAD_PAUSE = 1.0

_CONFIG = Config()
_SETTINGS = Settings()


class CaseControlServer:
    def __init__(self, args):
        self._keep_running = True
        self._keepalive_up = True
        self._debug = args.debug

        if self._debug:
            logger.setLevel(logging.DEBUG)

        # Init config/settings
        _CONFIG.init(args.config)
        _SETTINGS.init(args.settings)

        self._hw_data = HardwareData(BLACK, BLACK, '')  # The values that get written to hardware
        self._threads = []  # List of background threads to run

        # Import LCD/LED handlers based on whether or not we are mocking
        if args.mock:
            from .core.curses import CursesLcd as Lcd, CursesLed as Led  # FAKE HANDLERS, SAD!!
        elif args.null:
            from .core.null import NullLcd as Lcd, NullLed as Led
        else:
            from .lcd.lcd import Lcd
            from .led.led import Led

        # Init the LCD handler
        self._lcd = Lcd(_CONFIG.lcd_serial_device, _CONFIG.lcd_width, _CONFIG.lcd_height)

        # Init the LED handler
        self._led = Led()

        # Add background threads to be run
        self._add_thread(self._led_thread)
        self._add_thread(self._lcd_thread)
        self._add_thread(self._hw_data_thread, daemon=True)
        self._add_thread(self._ping_thread, args=(_CONFIG.keepalive_host,), daemon=True)

    def _add_thread(self, target, **kwargs):
        thread = threading.Thread(target=target, **kwargs)
        self._threads.append(thread)

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
        self._keep_running = False

        # Wait for all blocking (i.e. non-daemon) threads to terminate
        logger.debug("Waiting for threads to stop...")
        for thread in self._threads:
            if not thread.daemon:
                thread.join()

    def _led_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        try:
            while self._keep_running:
                color = self._hw_data.led_color if self._keepalive_up else BLACK
                self._led.set_color(color)
                time.sleep(_LED_THREAD_PAUSE)
        finally:
            self._led.stop()
            logger.debug("LED thread stopped")

    def _lcd_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        try:
            while self._keep_running:
                if self._keepalive_up:
                    color = self._hw_data.lcd_color
                    text = self._hw_data.lcd_text
                else:
                    color = BLACK
                    text = ''
                self._lcd.set_color(color)
                self._lcd.set_text(text)
                # self._lcd.flush_serial()  # Maybe uncomment this if we have problems?`
        finally:
            self._lcd.stop()
            logger.debug("LCD thread stopped")

    def _hw_data_thread(self):
        """
        @brief      A thread that periodically re-calculates the hardware data from the settings.

        @param      self  The object

        @return     None
        """
        while self._keep_running:
            # Compute new values and store them
            led_color = led_mode.get_color(_SETTINGS.get('led.mode'))
            lcd_color, lcd_text = lcd_mode.get_color_and_text(_SETTINGS.get('lcd.mode'))
            self._hw_data = HardwareData(led_color, lcd_color, lcd_text)
            time.sleep(_HW_DATA_THREAD_PAUSE)

    def _ping_thread(self, keepalive_host):
        """
        @brief      A thread that periodically pings the keepalive host. If the host doesn't repond,
                    the LED and LCD are shut off. If there is no host set, it is assumed to be up.

        @param      self  The object

        @return     None
        """
        while self._keep_running:
            success = True  # Assume true until we have a failing ping
            if keepalive_host:  # If a host was specified...
                exit_code = subprocess.call(['ping', '-c', '1', keepalive_host],
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                success = not exit_code

            # If the value changed, log it
            if success != self._keepalive_up:
                logger.debug(f"Keepalive up: {success}")
            self._keepalive_up = success

            time.sleep(_PING_THREAD_PAUSE)  # Until we meet again...
