import logging
import subprocess
import threading
import time
from collections import namedtuple

from ccs import app, logger
from .core.settings import Settings
from .core.color import BLACK
from .led.led_mode import LedMode
from .lcd.lcd_mode import LcdMode

HardwareData = namedtuple('HardwareData', 'led_color lcd_color lcd_text')
settings = Settings()


class CaseControlServer:
    _LED_THREAD_PAUSE = 0.01
    _LCD_THREAD_PAUSE = 0.01
    _HW_DATA_THREAD_PAUSE = 0.05
    _PING_THREAD_PAUSE = 1.0

    def __init__(self, args):
        self._run = True
        self._keepalive_up = True
        self._debug = args.debug

        if self._debug:
            logger.setLevel(logging.DEBUG)

        # Init config/settings
        settings.init(args.settings)

        self._hw_data = HardwareData(BLACK, BLACK, '')  # The values that get written to hardware

        # Import LCD/LED handlers based on whether or not we are mocking
        if args.mock:
            from .core.curses import CursesLcd as Lcd, CursesLed as Led  # FAKE HANDLERS, SAD!!
        elif args.null:
            from .core.null import NullLcd as Lcd, NullLed as Led
        else:
            from .lcd.lcd import Lcd
            from .led.led import Led

        # Init the LED/LCD handlers
        self._led = Led()
        self._lcd = Lcd(args.lcd_serial, args.lcd_width, args.lcd_height)

        # Add background threads to be run
        def add_thread(target, **kwargs):
            thread = threading.Thread(target=target, **kwargs)
            self._threads.append(thread)
        self._threads = []
        add_thread(self._led_thread)
        add_thread(self._lcd_thread)
        add_thread(self._hw_data_thread, daemon=True)
        add_thread(self._ping_thread, args=(args.keepalive,), daemon=True)

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

        @param      self  The object

        @return     None
        """
        try:
            while self._run:
                color = self._hw_data.led_color if self._keepalive_up else BLACK
                self._led.set_color(color)
                time.sleep(CaseControlServer._LED_THREAD_PAUSE)
            logger.debug("LED thread stopped")
        except Exception as e:
            logger.error(f"LED thread stopped with exception: {e}")
        finally:
            self._led.stop()

    def _lcd_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        try:
            while self._run:
                if self._keepalive_up:
                    color = self._hw_data.lcd_color
                    text = self._hw_data.lcd_text
                else:
                    color = BLACK
                    text = ''
                self._lcd.set_color(color)
                self._lcd.set_text(text)
                time.sleep(CaseControlServer._LCD_THREAD_PAUSE)
            logger.debug("LCD thread stopped")
        except Exception as e:
            logger.error(f"LCD thread stopped with exception: {e}")
        finally:
            self._lcd.stop()

    def _hw_data_thread(self):
        """
        @brief      A thread that periodically re-calculates the hardware data from the settings.

        @param      self  The object

        @return     None
        """
        while self._run:
            # Compute new values and store them
            led_color = LedMode.get_color(settings)
            lcd_color, lcd_text = LcdMode.get_color_and_text(self._lcd, settings)
            self._hw_data = HardwareData(led_color, lcd_color, lcd_text)
            time.sleep(CaseControlServer._HW_DATA_THREAD_PAUSE)

    def _ping_thread(self, keepalive_host):
        """
        @brief      A thread that periodically pings the keepalive host. If the host doesn't repond,
                    the LED and LCD are shut off. If there is no host set, it is assumed to be up.

        @param      self  The object

        @return     None
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
