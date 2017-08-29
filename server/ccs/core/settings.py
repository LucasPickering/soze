import abc
import pickle
import re

from ccs import logger
from .color import Color, unpack_color, BLACK
from .singleton import Singleton
from ccs.lcd import lcd_mode
from ccs.led import led_mode


class Named(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def get(self):
        pass

    @abc.abstractmethod
    def set(self, value):
        pass


class Section(Named):
    def __init__(self, name, *children):
        self._children = {child.name: child for child in children}
        super().__init__(name)

    def __getitem__(self, item):
        return self._children[item]

    def __setitem__(self, item, value):
        self._children[item].set(value)

    def get(self):
        # Convert children into a dict
        return {k: v.get() for k, v in self._children.items()}

    def set(self, value):
        raise AttributeError("Section cannot be set")


class Setting(Named):
    def __init__(self, name, default_val):
        super().__init__(name)
        self._val = default_val

    def __str__(self):
        val = self.get()
        return f"{name}: {val}"

    def get(self):
        return self._val

    def set(self, value):
        validated = self._validate()
        self._val = validated
        return validated

    def _validate(self, val):
        return val


class ModeSetting(Setting):
    def __init__(self, name, valid_modes, default_mode='off'):
        super().__init__(name, default_mode)
        self._valid_modes = valid_modes

    def _is_valid(self, val):
        if not isinstance(val, str):
            raise ValueError(f"Expected str, got {val}")
        if val not in self._valid_modes:
            raise ValueError(f"Expected one of {self._valid_modes}, got {val}")
        return val.lower()


class ColorSetting(Setting):
    def __init__(self, name, default_color=BLACK):
        super().__init__(name, default_color)

    def _validate(self, val):
        if not isinstance(val, Color):
            val = unpack_color(val)  # This will raise an error if it isn't unpackable
        return val


def _new_settings():
    return \
        Section('',
                Section('led',
                        ModeSetting('mode', led_mode.MODES),
                        Section('static',
                                ColorSetting('color')
                                )
                        ),
                Section('lcd',
                        ModeSetting('mode', lcd_mode.MODES),
                        ColorSetting('color')
                        )
                )


class Settings(metaclass=Singleton):
    """
    @brief      The settings directly determined by the user. These are all set from the API.
                They are used to calculatate the data sent to the hardware.
                LED and LCD mode are examples of user settings.
    """

    def __init__(self):
        self._settings = _new_settings()

    def init(self, settings_file):
        # This is separate from the constructor so that anyone can use get this instance via the
        # constructor without having to initialize the class

        self._settings_file = settings_file

        # Init default values for properties
        self._settings = _new_settings()

        self._load()  # Load from the settings file
        self._save()  # Write the whole settings file to make sure it's up to date

    def _get_at_path(self, path):
        d = self._settings

        if path:
            # Drill down into the settings
            for key in re.split(r'[./]', path):  # Split on . or /
                try:
                    d = d[key]
                except KeyError:
                    raise ValueError(f"Invalid path: {path}")

        return d  # Return the section/setting that we ended up with

    def get(self, path):
        return self._get_at_path(path).get()

    def set(self, path, value):
        obj = self._get_at_path(value)
        obj.set(value)
        self._on_setting_changed()

    def _on_setting_changed(self, setting):
        val = setting.get()
        logger.info(f"Setting {setting.name} to {val}")
        self._save()

    def _load(self):
        # Load the dict from a file
        try:
            with open(self._settings_file, 'rb') as f:
                self._settings = pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings from '{self._settings_file}': {e}")

    def _save(self):
        # Save settings to a file
        logger.debug(f"Saving settings to '{self._settings_file}'")
        with open(self._settings_file, 'wb') as f:
            pickle.dump(self._settings, f)
