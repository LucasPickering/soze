import abc
import inspect
import re

MODE_NAME_RGX = re.compile(r'(.+)Mode')
MODES = {}


class LcdModeMeta(abc.ABCMeta):
    def __new__(cls, clsname, bases, attrs):
        newclass = super().__new__(cls, clsname, bases, attrs)
        if not inspect.isabstract(newclass):
            m = MODE_NAME_RGX.match(clsname)
            if not m:
                raise ValueError("Mode class name must match {}".format(MODE_NAME_RGX.pattern))
            name = m.group(1).lower()
            MODES[name] = newclass()  # Instantiate the class and register the object
        return newclass


class LcdMode(metaclass=LcdModeMeta):

    def _get_color(self, lcd, settings):
        return settings.get('lcd.color')

    @abc.abstractmethod
    def _get_text(self, lcd, settings):
        pass

    @staticmethod
    def get_mode_names():
        return set(MODES.keys())

    @staticmethod
    def get_color_and_text(lcd, settings):
        """
        @brief      Gets the current color and text for the LCD.

        @param      settings  The current settings

        @return     The current LCD color and text, in a tuple, based on mode and other settings.

        @raise     ValueError if the given LCD mode is unknown
        """
        mode = MODES[settings.get('lcd.mode')]  # Get the relevant mode object
        return (mode._get_color(lcd, settings), mode._get_text(lcd, settings))
