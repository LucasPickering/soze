import configparser
import json

import led_mode
import lcd_mode
from color import Color, unpack_color


class Config:

    DEFAULT_CFG_FILE = 'default.ini'

    def __init__(self, logger, cfg_file_name):
        self.logger = logger

        # Read config values from default file, then user file
        config = configparser.SafeConfigParser()
        config.read(self.DEFAULT_CFG_FILE)
        config.read(cfg_file_name)

        # Print loaded values
        cfg_dict = {sct: dict(config.items(sct)) for sct in config.sections()}
        self.logger.info("Loaded config: {}".format(cfg_dict))

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

    def __init__(self, settings_file, logger, config):
        self.settings_file = settings_file
        self.logger = logger
        self.config = config

        # Init default values
        self.set_led_mode('off', save=False)
        self.set_led_static_color(Color(0, 0, 0), save=False)
        self.set_lcd_mode('off', save=False)
        self.set_lcd_color(Color(0, 0, 0), save=False)

        # Try to load from settings, if that fails, the default values stay
        try:
            self.load()
        except Exception as e:
            raise(e)  # TODO remove
            self.logger.warning("Failed to load from settings file '{}': {}".format(settings_file,
                                                                                    e))

        self.save()  # Save everything now

    def __setting_changed(self, setting, value, save):
        self.logger.info("Setting '{}' to '{}'".format(setting, value))
        if save:
            self.save()

    def set_led_mode(self, mode_name, save=True):
        self.led_mode = led_mode.get_by_name(mode_name, self.config, self)
        self.__setting_changed("LED mode", mode_name, save)

    def set_led_static_color(self, color, save=True):
        if type(color) is not Color:
            color = unpack_color(color)
        self.led_static_color = color
        self.__setting_changed("LED static color", color, save)

    def set_lcd_mode(self, mode_name, save=True):
        self.lcd_mode = lcd_mode.get_by_name(mode_name, self.config, self)
        self.__setting_changed("LCD mode", mode_name, save)

    def set_lcd_color(self, color, save=True):
        if type(color) is not Color:
            color = unpack_color(color)
        self.lcd_color = color
        self.__setting_changed("LCD color", color, save)

    def __make_settings_dict(self):
        """
        @brief      Puts all of this object's settings in a dict

        @param      self  The object

        @return     a dict containing this object's settings
        """
        d = dict()
        d['led_mode'] = self.led_mode.NAME
        d['led_static_color'] = self.led_static_color
        d['lcd_mode'] = self.lcd_mode.NAME
        d['lcd_color'] = self.lcd_color
        return d

    __SETTINGS = {
        'led_mode': set_led_mode,
        'led_static_color': set_led_static_color,
        'lcd_mode': set_lcd_mode,
        'lcd_color': set_lcd_color
    }

    def load(self):
        # Load the dict from a file
        with open(self.settings_file, 'r') as f:
            cfg_dict = json.load(f)
        for k, v in cfg_dict.items():
            setter = self.__SETTINGS[k]
            setter(self, v, save=False)

    def save(self):
        # Copy this object's dict and delete the fields we don't want to save
        d = self.__make_settings_dict()

        # Save the dict to a file
        self.logger.debug("Saving settings to '{}'".format(self.settings_file))
        with open(self.settings_file, 'w') as f:
            json.dump(d, f, indent=4)


class DerivedSettings:
    """
@brief      Derived settings are the settings that are calulacted from the user settings. These are
            the settings that actually get pushed to the LEDs and LCD. These are NOT directly
            modifiable by the user. They are regularly (many times per second) updated based on
            the current user settings, by a dedicated thread.
"""

    def __init__(self, logger, user_settings):
        self.logger = logger
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
