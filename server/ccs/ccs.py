import argparse
import logging
import subprocess
import threading
import time

from ccs import app, logger
from .core import settings
from .core.color import BLACK


class CaseControlServer:

    LED_THREAD_PAUSE = 0.01
    LCD_THREAD_PAUSE = 0.01
    SETTINGS_THREAD_PAUSE = 0.05
    PING_THREAD_PAUSE = 1.0

    def __init__(self, args):
        self.keep_running = True
        self.keepalive_up = True
        self.debug = args.debug

        if self.debug:
            logger.setLevel(logging.DEBUG)

        # Init config/settings
        self.config = settings.Config()
        self.config.init(args.config)
        self.user_settings = settings.UserSettings()
        self.user_settings.init(args.settings)
        self.derived_settings = settings.DerivedSettings()

        # Import LCD/LED handles based on whether or not we are mocking
        if args.mock:
            from .core.mock import MockedLcd as Lcd, MockedLed as Led
        else:
            from .lcd.lcd import Lcd
            from .led.led import Led

        # Init the case LED handler
        self.led = Led()

        # This thread constantly reads the derived settings and updates the LEDs accordingly
        self.led_thrd = threading.Thread(target=self.led_thread)

        # Init the LCD handler
        self.lcd = Lcd(self.config.lcd_serial_device,
                       self.config.lcd_width, self.config.lcd_height)
        self.lcd.set_autoscroll(False)
        self.lcd.on()
        self.lcd.clear()

        # This thread constantly reads the derived settings and updates the LCD accordingly
        self.lcd_thrd = threading.Thread(target=self.lcd_thread)

        # This thread constantly re-computes the derived settings from the user settings
        self.settings_thrd = threading.Thread(target=self.settings_thread, daemon=True)

        self.ping_thrd = threading.Thread(target=self.ping_thread, daemon=True)

    def run(self):
        # Start the helper threads, then launch the REST API
        self.led_thrd.start()
        self.lcd_thrd.start()
        self.settings_thrd.start()
        self.ping_thrd.start()
        try:
            app.run(host='0.0.0.0', debug=self.debug, use_reloader=False)
        finally:
            # When flask receives Ctrl-C and stops, this runs to shut down the other threads
            self.stop()

    def stop(self):
        logger.info("Stopping...")
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
            logger.error(e)
        self.led.stop()
        logger.info("LED thread stopped")

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
        logger.info("LCD thread stopped")

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
                        logger.debug("Keepalive down")
                    self.keepalive_up = False
                    continue
            if not self.keepalive_up:
                logger.debug("Keepalive up")
            self.keepalive_up = True


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
