import abc
import pickle

from ccs import logger
from .color import Color, BLACK
from ccs.lcd.lcd_mode import LcdMode
from ccs.led.led_mode import LedMode


class Setting(metaclass=abc.ABCMeta):
    def __init__(self, default_val):
        self.set(default_val)

    def get(self):
        return self._val

    def set(self, value):
        validated = self._validate(value)
        self._val = validated
        return self.get()

    @abc.abstractmethod
    def _validate(self, val):
        pass

    def __str__(self):
        return str(self._val)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._val}>"


class ListSetting(Setting):
    def __init__(self, setting, default_val=[]):
        super().__init__(default_val)
        self._setting = setting

    def _validate(self, val):
        if not isinstance(val, list):
            raise ValueError(f"Expected list, got {val}")
        return [self._setting._validate(e) for e in val]


class ModeSetting(Setting):
    def __init__(self, valid_modes, default_mode='off'):
        super().__init__(default_mode)
        self._valid_modes = valid_modes

    def _validate(self, val):
        if not isinstance(val, str):
            raise ValueError(f"Expected str, got {val}")
        val = val.lower()
        if val not in self._valid_modes:
            raise ValueError(f"Expected one of {self._valid_modes}, got {val}")
        return val


class ColorSetting(Setting):
    def __init__(self, default_color=BLACK):
        super().__init__(default_color)

    def _validate(self, val):
        if not isinstance(val, Color):
            val = Color.unpack(val)  # This will raise an error if it isn't unpackable
        return val


class Settings:
    """
    @brief      The settings directly determined by the user. These are all set from the API.
                They are used to calculatate the data sent to the hardware.
                LED and LCD mode are examples of user settings.
    """

    def init(self, settings_file):
        # This is separate from the constructor so that the object can be initialized with the
        # settings file name (as it is in __init__.py)

        self._settings_file = settings_file

        # Try to load from the file, if that fails, use default settings
        if not self._load():  # Try to load settings from file
            logger.debug("Initializing new settings...")
            self._settings = Settings._new_settings()
            self._save()  # Save the default settings

    @staticmethod
    def _new_settings():
        return {
            'led': {
                'mode': ModeSetting(LedMode.get_mode_names()),
                'static': {
                    'color': ColorSetting(),
                },
                'fade': {
                    'colors': ListSetting(ColorSetting()),
                },
            },
            'lcd': {
                'mode': ModeSetting(LcdMode.get_mode_names()),
                'color': ColorSetting(),
            },
        }

    def _get_at_path(self, path):
        path = path.replace('.', '/')
        d = self._settings
        name = ''

        # Drill down into the settings
        if path:
            for key in path.split('/'):  # Split on . or /
                try:
                    d = d[key]
                except KeyError:
                    raise ValueError(f"Invalid path: '{path}'")
                name = key

        return (name, d)  # Return the name and object that we ended up with

    def get(self, path):
        def get_all(obj):
            if isinstance(obj, Setting):
                return obj.get()
            return {k: get_all(v) for k, v in obj.items()}

        name, obj = self._get_at_path(path)
        return get_all(obj)

    def set(self, path, value):
        def set_all(obj, value):
            if isinstance(obj, Setting):
                return obj.set(value)
            if not isinstance(value, dict):
                raise ValueError("Value must be dict")
            return {k: set_all(obj[k], v) for k, v in value.items()}

        name, obj = self._get_at_path(path)
        rv = set_all(obj, value)
        self._on_setting_changed(path, rv)
        return rv

    def _on_setting_changed(self, name, value):
        logger.info(f"Setting {name} to {value}")
        self._save()

    def _load(self):
        """
        Load settings from the given pickle file.

        Return True if the settings were successfully loaded, False otherwise.
        """
        try:
            with open(self._settings_file, 'rb') as f:
                self._settings = pickle.load(f)
                logger.info(f"Loaded settings from '{self._settings_file}'")
                return True
        except Exception as e:
            logger.warning(f"Failed to load settings from '{self._settings_file}': {e}")
            return False

    def _save(self):
        """
        Save settings to the given pickle file.

        Return True if the settings were successfully saved, False otherwise.
        """
        try:
            with open(self._settings_file, 'wb') as f:
                pickle.dump(self._settings, f)
                logger.debug(f"Saved settings to '{self._settings_file}'")
                return True
        except Exception as e:
            logger.warning(f"Failed to save settings to '{self._settings_file}': {e}")
            return False
