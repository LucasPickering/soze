import configparser

from color import Color
import led_mode
import lcd_mode


class Config:

    DEFAULT_CFG_FILE = 'default.ini'

    def __init__(self, cfg_file_name):
        # Read config values from default file, then user file
        config = configparser.SafeConfigParser()
        config.read(self.DEFAULT_CFG_FILE)
        config.read(cfg_file_name)

        # Print loaded values
        cfg_dict = {sct: config.items(sct) for sct in config.sections()}
        print("Loaded config: {}".format(cfg_dict))

        # Load values
        self.lcd_serial_device = config.get('lcd', 'serial_device')
        self.lcd_width = config.getint('lcd', 'width')
        self.lcd_height = config.getint('lcd', 'height')

        # Save the config back to the file
        with open(cfg_file_name, 'w') as f:
            config.write(f)


class UserSettings:
    """
@brief      User settings are (unsurprisingly) the settings directly determined by the user. These
            are all set from the API. They are used to calculatate the derived settings. LED and
            LCD mode are examples of user settings.
"""

    def __init__(self, config):
        self.config = config
        self.led_mode = led_mode.LedModeOff(config, self)
        self.led_static_color = Color(0, 0, 0)
        self.lcd_mode = lcd_mode.LcdModeOff(config, self)
        self.lcd_color = Color(0, 0, 0)

    def set_led_mode(self, mode_name):
        self.led_mode = led_mode.get_by_name(mode_name, self.config, self)

    def set_led_static_color(self, color):
        self.led_static_color = color

    def set_lcd_mode(self, mode_name):
        self.lcd_mode = lcd_mode.get_by_name(mode_name, self.config, self)

    def set_lcd_color(self, color):
        self.lcd_color = color


class DerivedSettings:
    """
@brief      Derived settings are the settings that are calulacted from the user settings. These are
            the settings that actually get pushed to the LEDs and LCD. These are NOT directly
            modifiable by the user. They are regularly (many times per second) updated based on
            the current user settings, by a dedicated thread.
"""

    def __init__(self, user_settings):
        self.user_settings = user_settings
        self.led_color = Color(0, 0, 0)
        self.lcd_color = Color(0, 0, 0)
        self.lcd_text = ''

    def update(self):
        """
        @brief      Recalculates the derived settings based on the current user settings.

        @param      self  The object

        @return     None
        """
        self.led_color = self.user_settings.led_static_color
        self.lcd_color = self.user_settings.lcd_mode.get_color()
        self.lcd_text = self.user_settings.lcd_mode.get_text()
