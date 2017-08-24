import argparse
import logging
import subprocess
import threading
import time

from ccs import app, logger
from .core import config, user_settings, derived_settings
from .core.color import BLACK


class CaseControlServer:

    LED_THREAD_PAUSE = 0.01
    LCD_THREAD_PAUSE = 0.01
    SETTINGS_THREAD_PAUSE = 0.05
    PING_THREAD_PAUSE = 1.0

    def __init__(self, args):
        self._keep_running = True
        self._keepalive_up = True
        self._debug = args.debug

        if self._debug:
            logger.setLevel(logging.DEBUG)

        # Init config/settings
        config.init(args.config)
        user_settings.init(args.settings)

        self._threads = []  # List of background threads to run

        # Import LCD/LED handles based on whether or not we are mocking
        if args.mock:
            from .core.mock import MockedLcd as Lcd, MockedLed as Led
        else:
            from .lcd.lcd import Lcd
            from .led.led import Led

        # Init the LCD handler
        self._lcd = Lcd(config.lcd_serial_device, config.lcd_width, config.lcd_height)

        # Init the LED handler
        self._led = Led()

        # Add background threads to be run
        self._add_thread(self._led_thread)
        self._add_thread(self._lcd_thread)
        self._add_thread(self._settings_thread, daemon=True)
        self._add_thread(self._ping_thread, args=(config.keepalive_host,), daemon=True)

    def _add_thread(self, target, **kwargs):
        thread = threading.Thread(target=target, **kwargs)
        self._threads.append(thread)

    def run(self):
        # Start the helper threads, then launch the REST API
        for thread in self._threads:
            thread.start()
        try:
            app.run(host='0.0.0.0', debug=self._debug, use_reloader=False)
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
        while self._keep_running:
            color = derived_settings.led_color if self._keepalive_up else BLACK
            self._led.set_color(color.red, color.green, color.blue)
            time.sleep(self.LED_THREAD_PAUSE)
        self._led.stop()
        logger.debug("LED thread stopped")

    def _lcd_thread(self):
        """
        @brief      A thread that periodically updates the case LEDs based on the current
                    derived settings.

        @param      self  The object

        @return     None
        """
        while self._keep_running:
            if self._keepalive_up:
                color = derived_settings.lcd_color
                text = derived_settings.lcd_text
            else:
                color = BLACK
                text = ''
            self._lcd.set_color(color)
            self._lcd.set_text(text)
            # self._lcd.flush_serial()  # Maybe uncomment this if we have problems?`
        self._lcd.off()
        self._lcd.clear()
        self._lcd.stop()
        logger.debug("LCD thread stopped")

    def _settings_thread(self):
        """
        @brief      A thread that periodically re-calculates the derived settings. These settings
                    are calculated from the user settings.

        @param      self  The object

        @return     None
        """
        while self._keep_running:
            derived_settings.update()
            time.sleep(self.SETTINGS_THREAD_PAUSE)

    def _ping_thread(self, keepalive_host):
        """
        @brief      A thread that periodically pings the keepalive host. If the host doesn't repond,
                    the LED and LCD are shut off. If there is no host set, it is assumed to be up.

        @param      self  The object

        @return     None
        """
        while self._keep_running:
            time.sleep(self.PING_THREAD_PAUSE)
            if keepalive_host:
                exit_code = subprocess.call(['ping', '-c', '1', keepalive_host],
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if exit_code:
                    if self._keepalive_up:
                        logger.debug("Keepalive down")
                    self._keepalive_up = False
                    continue
            if not self._keepalive_up:
                logger.debug("Keepalive up")
            self._keepalive_up = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('-c', '--config', default='config.ini', help="Specify the config file")
    parser.add_argument('-m', '--mock', action='store_const', default=False, const=True,
                        help="Run in mocking mode, for testing without all the hardware")
    parser.add_argument('-s', '--settings', default='settings.json',
                        help="Specify the settings file that will be saved to and loaded from")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()
