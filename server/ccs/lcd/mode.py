import abc
import inspect
import re

_MODE_NAME_RGX = re.compile(r'(.+)Mode')
_MODES = {}


class LcdModeMeta(abc.ABCMeta):
    def __new__(cls, clsname, bases, attrs):
        newclass = super().__new__(cls, clsname, bases, attrs)
        if not inspect.isabstract(newclass):
            m = _MODE_NAME_RGX.match(clsname)
            if not m:
                raise ValueError("Mode class name must match {}".format(_MODE_NAME_RGX.pattern))
            name = m.group(1).lower()
            _MODES[name] = newclass()  # Instantiate the class and register the object
        return newclass


class LcdMode(metaclass=LcdModeMeta):

    def _get_color(self, settings):
        return settings.get('lcd.color')

    @abc.abstractmethod
    def _get_text(self, settings):
        pass

    @staticmethod
    def get_mode_names():
        return set(_MODES.keys())

    @staticmethod
    def get_color_and_text(settings):
        """
        @brief      Gets the current color and text for the LCD.

        @param      settings  The current settings

        @return     The current LCD color and text, in a tuple, based on mode and other settings.

        @raise      ValueError if the given LCD mode is unknown
        """
        mode = _MODES[settings.get('lcd.mode')]  # Get the relevant mode object
        return (mode._get_color(settings), mode._get_text(settings))
