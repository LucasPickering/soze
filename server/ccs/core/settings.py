import abc
import copy
import os
import pickle

from ccs import logger
from .color import Color, BLACK
from ccs.lcd.mode import LcdMode
from ccs.led.mode import LedMode


class Setting(metaclass=abc.ABCMeta):
    def __init__(self, default_val):
        self.set(default_val)

    def get(self, serialized):
        return self._serialize(self._val) if serialized else self._val

    def set(self, value):
        self._val = self._deserialize(value)
        return self.get(serialized=True)

    def _serialize(self, val):
        return val

    @abc.abstractmethod
    def _deserialize(self, val):
        pass

    def __str__(self):
        return str(self._val)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._val}>"


class ModeSetting(Setting):
    def __init__(self, mode_class, default_mode='off'):
        self._mode_class = mode_class
        super().__init__(default_mode)

    def _serialize(self, val):
        return val.name

    def _deserialize(self, val):
        if isinstance(val, str):
            try:
                cls = self._mode_class.get_by_name(val.lower())
                return cls()  # Instantiate the class
            except KeyError:
                valid_modes = self._mode_class.get_mode_names()
                raise ValueError(f"Expected one of {valid_modes}, got {val}")
        raise ValueError(f"Expected str, got {val}")


class ColorSetting(Setting):
    def __init__(self, default_color=BLACK):
        super().__init__(default_color)

    def _serialize(self, val):
        return val.to_hex_str()

    def _deserialize(self, val):
        if not isinstance(val, Color):
            val = Color.unpack(val)  # This will raise an error if it isn't unpackable
        return val


class BoolSetting(Setting):
    def __init__(self, default_val=False):
        super().__init__(default_val)

    def _deserialize(self, val):
        if not isinstance(val, bool):
            raise ValueError(f"Expected bool, got {val}")
        return val


class FloatSetting(Setting):
    def __init__(self, default_val, min_=None, max_=None):
        self._min = min_
        self._max = max_
        super().__init__(default_val)

    def _deserialize(self, val):
        if not isinstance(val, float):
            raise ValueError(f"Expected float, got {val}")
        if self._min is not None and val < self._min:
            raise ValueError(f"Value {val} below minimum of {self._min}")
        if self._max is not None and val > self._max:
            raise ValueError(f"Value {val} below maximum of {self._max}")
        return val


class ListSetting(Setting):
    def __init__(self, setting, default_val=[]):
        self._setting = setting
        super().__init__(default_val)

    def _serialize(self, val):
        return [self._setting._serialize(e) for e in val]

    def _deserialize(self, val):
        if not isinstance(val, list):
            raise ValueError(f"Expected list, got {val}")
        return [self._setting._deserialize(e) for e in val]


class DictSetting(Setting):
    def __init__(self, setting, default_val={}):
        self._setting = setting
        super().__init__(default_val)

    def _serialize(self, val):
        return {k: self._setting._serialize(v) for k, v in val.items()}

    def _deserialize(self, val):
        if not isinstance(val, dict):
            raise ValueError(f"Expected dict, got {val}")
        return {k: v._deserialize(v) for k, v in val.items()}


class Settings:
    """
    @brief      The settings directly determined by the user. These are all set from the API.
                They are used to calculatate the data sent to the hardware.
                LED and LCD mode are examples of user settings.
    """

    SETTINGS_FILE = 'settings.p'
    DEFAULT_SETTINGS = {
        'led': {
            'mode': ModeSetting(LedMode),
            'static': {
                'color': ColorSetting(),
            },
            'fade': {
                'colors': ListSetting(ColorSetting()),
                'saved': DictSetting(ListSetting(ColorSetting())),
                'fade_time': FloatSetting(5.0, 1.0, 30.0),
            },
        },
        'lcd': {
            'mode': ModeSetting(LcdMode),
            'color': ColorSetting(),
            'link_to_led': BoolSetting(),
        },
    }

    def init(self, settings_dir):
        """
        @brief      Initialize the settings object. This is separate from the constructor so that
                    the object can be constructed without being initialized.

        @param      settings_dir  The directory to contain the settings file
        """
        self._settings_file = os.path.join(settings_dir, Settings.SETTINGS_FILE)
        self._settings = copy.deepcopy(Settings.DEFAULT_SETTINGS)

        self._load()
        self._save()  # Save in case anything changed

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

    def get(self, path, serialized=False):
        def get_all(obj):
            if isinstance(obj, Setting):
                return obj.get(serialized)
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
        try:
            rv = set_all(obj, value)
        except KeyError as e:
            raise KeyError(f"Unknown setting: {e}")
        self._on_setting_changed(path, rv)
        return rv

    def _on_setting_changed(self, name, value):
        logger.debug(f"Set {name} to {value}")
        self._save()

    def _load(self):
        """
        @brief      Loads settings from the settings file. Only values loaded from the pickle
                    settings are updated; any value in the default settings but not the pickle
                    ones does not get deleted. Any value in the pickle settings but not the
                    defaults does not get included at all. This indicates that a setting was
                    renamed or removed.
        """
        def update_dict(base, new):
            for k, v in new.items():
                if k in base:  # Exclude things that only appear in the new dict
                    base_v = base[k]
                    if type(base_v) == type(v):  # If the type differs, stick with the base value
                        if isinstance(v, dict):  # RECURSION
                            update_dict(base_v, v)
                        else:
                            base[k] = v
        try:
            with open(self._settings_file, 'rb') as f:
                loaded = pickle.load(f)
            update_dict(self._settings, loaded)
            logger.info(f"Loaded settings from '{self._settings_file}'")
        except Exception as e:
            logger.warning(f"Failed to load settings from '{self._settings_file}': {e}")

    def _save(self):
        """
        @brief      Saves the current settings to the settings file.
        """
        try:
            with open(self._settings_file, 'wb') as f:
                pickle.dump(self._settings, f)
            logger.debug(f"Saved settings to '{self._settings_file}'")
        except Exception as e:
            logger.warning(f"Failed to save settings to '{self._settings_file}': {e}")
