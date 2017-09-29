import abc
import inspect
import re

_MODE_NAME_RGX = re.compile(r'(.+)Mode')
_MODES = {}


class LedModeMeta(abc.ABCMeta):
    def __new__(cls, clsname, bases, attrs):
        newclass = super().__new__(cls, clsname, bases, attrs)
        if not inspect.isabstract(newclass):
            m = _MODE_NAME_RGX.match(clsname)
            if not m:
                raise ValueError("Mode class name must match {}".format(_MODE_NAME_RGX.pattern))
            name = m.group(1).lower()
            _MODES[name] = newclass()  # Instantiate the class and register the object
        return newclass


class LedMode(metaclass=LedModeMeta):

    @abc.abstractmethod
    def _get_color(self, settings):
        pass

    @staticmethod
    def get_mode_names():
        return set(_MODES.keys())

    @staticmethod
    def get_color(settings):
        """
        @brief      Gets the current color for the LEDs.

        @param      settings  The current settings

        @return     The current LED color, based on mode and other relevant settings.

        @raise      ValueError if the given LED mode is unknown
        """
        mode = _MODES[settings.get('led.mode')]  # Get the relevant mode object
        return mode._get_color(settings)
