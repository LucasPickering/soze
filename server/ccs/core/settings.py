import json

from .. import logger
from .color import Color, unpack_color, BLACK
from .singleton import Singleton


class Settings(metaclass=Singleton):
    """
    @brief      The settings directly determined by the user. These are all set from the API.
                They are used to calculatate the data sent to the hardware.
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
    def led_mode(self, led_mode):
        self._led_mode = led_mode.lower()

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
    def lcd_mode(self, lcd_mode):
        self._lcd_mode = lcd_mode.lower()

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
            with open(self._settings_file, 'r') as f:
                settings_dict = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings from '{self._settings_file}': {e}")
            settings_dict = dict()

        self.__dict__.update(settings_dict)

    def _save(self):
        # Save settings to a file
        logger.debug(f"Saving settings to '{self._settings_file}'")
        with open(self._settings_file, 'w') as f:
            json.dump(vars(self), f, indent=4)
