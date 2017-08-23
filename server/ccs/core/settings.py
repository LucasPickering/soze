import configparser
import json
import pickle

from .. import logger
from .color import Color, unpack_color, BLACK
from .singleton import Singleton
from ccs.lcd import lcd_mode
from ccs.led import led_mode


class Config(metaclass=Singleton):

    DEFAULT_CFG_FILE = 'default.ini'

    def init(self, cfg_file):
        # This is separate from the constructor so that anyone can use get this instance via the
        # constructor without having to initialize the class

        # Read config values from default file, then user file
        config = configparser.SafeConfigParser()
        config.read(self.DEFAULT_CFG_FILE)
        config.read(cfg_file)

        # Print loaded values
        cfg_dict = {sct: dict(config.items(sct)) for sct in config.sections()}
        logger.info(f"Loaded config: {cfg_dict}")

        # Load values
        self.keepalive_host = config.get('main', 'keepalive_host')
        self.lcd_serial_device = config.get('lcd', 'serial_device')
        self.lcd_width = config.getint('lcd', 'width')
        self.lcd_height = config.getint('lcd', 'height')

        # Save the config back to the file
        with open(cfg_file, 'w') as f:
            config.write(f)


class UserSettings(metaclass=Singleton):
    """
    @brief      User settings are (unsurprisingly) the settings directly determined by the user.
                These are all set from the API. They are used to calculatate the derived settings.
                LED and LCD mode are examples of user settings.
    """

    def __init__(self):
        self._init = False

    def init(self, settings_file):
        # This is separate from the constructor so that anyone can use get this instance via the
        # constructor without having to initialize the class

        self._settings_file = settings_file

        # Init default values for fields
        self.led_mode = 'off'
        self.led_static_color = BLACK
        self.lcd_mode = 'off'
        self.lcd_color = BLACK

        self._load()  # Load from the settings file
        self._save()  # Write the whole settings file to make sure it's up to date
        self._init = True

    def __setattr__(self, attr, value):
        super().__setattr__(attr, value)
        if attr[0] != '_':  # GREAT CODE
            logger.info(f"Setting '{attr}' to '{value}'")
            if self._init:  # We don't want to save during setup because it causes problemos
                self._save()

    @property
    def led_mode(self):
        return self._led_mode

    @led_mode.setter
    def led_mode(self, mode_name):
        self._led_mode = led_mode.get_by_name(mode_name)

    @property
    def led_static_color(self):
        return self._led_static_color

    @led_static_color.setter
    def led_static_color(self, color):
        if type(color) is not Color:
            color = unpack_color(color)
        self._led_static_color = color

    @property
    def lcd_mode(self):
        return self._lcd_mode

    @lcd_mode.setter
    def lcd_mode(self, mode_name):
        self._lcd_mode = lcd_mode.get_by_name(mode_name)

    @property
    def lcd_color(self):
        return self._lcd_color

    @lcd_color.setter
    def lcd_color(self, color):
        if type(color) is not Color:
            color = unpack_color(color)
        self._lcd_color = color

    def _load(self):
        # Load the dict from a file
        try:
            with open(self._settings_file, 'rb') as f:
                settings_dict = pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings from '{self._settings_file}': {e}")
            settings_dict = dict()

        self.__dict__.update(settings_dict)

    def _save(self):
        # Save settings to a file
        logger.debug(f"Saving settings to '{self._settings_file}'")
        with open(self._settings_file, 'wb') as f:
            pickle.dump(vars(self), f)


class DerivedSettings(metaclass=Singleton):
    """
    @brief      Derived settings are the settings that are calulacted from the user settings.
                These are the settings that actually get pushed to the LEDs and LCD. These are NOT
                directly modifiable by the user. They are regularly (many times per second) updated
                based on the current user settings, by a dedicated thread.
    """

    def __init__(self):
        self.user_settings = UserSettings()
        self.led_color = BLACK
        self.lcd_color = BLACK
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
