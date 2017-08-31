import pickle

from ccs import logger
from .color import Color, unpack_color, BLACK
from .singleton import Singleton
from ccs.lcd import lcd_mode
from ccs.led import led_mode


class Setting:
    def __init__(self, default_val):
        self._val = default_val

    def get(self):
        return self._val

    def set(self, value):
        validated = self._validate(value)
        self._val = validated
        return validated

    def _validate(self, val):
        return val


class ModeSetting(Setting):
    def __init__(self, valid_modes, default_mode='off'):
        super().__init__(default_mode)
        self._valid_modes = valid_modes

    def _is_valid(self, val):
        if not isinstance(val, str):
            raise ValueError(f"Expected str, got {val}")
        if val not in self._valid_modes:
            raise ValueError(f"Expected one of {self._valid_modes}, got {val}")
        return val.lower()


class ColorSetting(Setting):
    def __init__(self, default_color=BLACK):
        super().__init__(default_color)

    def _validate(self, val):
        if not isinstance(val, Color):
            val = unpack_color(val)  # This will raise an error if it isn't unpackable
        return val


def _new_settings():
    return {
        'led': {
            'mode': ModeSetting(led_mode.MODES),
            'static': {
                'color': ColorSetting(),
            },
        },
        'lcd': {
            'mode': ModeSetting(lcd_mode.MODES),
            'color': ColorSetting()
        },
    }


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
