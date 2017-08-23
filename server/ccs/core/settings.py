import configparser
import json
from collections import namedtuple

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

        self.settings_file = settings_file
        self.config = Config()

        self.load()  # Load from the settings file
        self.save()  # Write the whole settings file to make sure it's up to date
        self._init = True

    def _setting_changed(self, setting, value):
        logger.info(f"Setting '{setting}' to '{value}'")
        if self._init:  # We don't want to save during setup because it causes problemos
            self.save()

    def set_led_mode(self, mode_name):
        self.led_mode = led_mode.get_by_name(mode_name, self.config, self)
        self._setting_changed("LED mode", mode_name)

    def set_led_static_color(self, color):
        if type(color) is not Color:
            color = unpack_color(color)
        self.led_static_color = color
        self._setting_changed("LED static color", color)

    def set_lcd_mode(self, mode_name):
        self.lcd_mode = lcd_mode.get_by_name(mode_name, self.config, self)
        self._setting_changed("LCD mode", mode_name)

    def set_lcd_color(self, color):
        if type(color) is not Color:
            color = unpack_color(color)
        self.lcd_color = color
        self._setting_changed("LCD color", color)

    Setting = namedtuple('Setting', 'default_value getter setter')
    _SETTINGS = {
        'led': {
            'led_mode': Setting('off',
                                lambda self: self.led_mode.NAME,
                                set_led_mode),
            'led_static_color': Setting(BLACK,
                                        lambda self: self.led_static_color,
                                        set_led_static_color),
        },
        'lcd': {
            'lcd_mode': Setting('off',
                                lambda self: self.lcd_mode.NAME,
                                set_lcd_mode),
            'lcd_color': Setting(BLACK,
                                 lambda self: self.lcd_color,
                                 set_lcd_color)
        }
    }

    def to_dict(self):
        # Create a dict for each section, then put all those sections into one big ol' dict
        d = dict()
        for section_name, section in self._SETTINGS.items():
            # Make a dict for this section
            d[section_name] = {name: setting.getter(self) for name, setting in section.items()}
        return d

    def load(self):
        # Load the dict from a file
        try:
            with open(self.settings_file, 'r') as f:
                settings_dict = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings from '{self.settings_file}': {e}")
            settings_dict = dict()

        # Try to read each section from the settings file. For each setting in each section, try to
        # read that setting from the section. If it isn't in the settings file, use the default.
        for section_name, section in self._SETTINGS.items():
            section_vals = settings_dict.get(section_name, dict())
            for setting_name, setting in section.items():
                setting.setter(self, section_vals.get(setting_name, setting.default_value))

    def save(self):
        # Save settings to a file
        logger.debug(f"Saving settings to '{self.settings_file}'")
        with open(self.settings_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)


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
