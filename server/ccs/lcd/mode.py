import abc

MODES = {}


class LcdMode(metaclass=abc.ABCMeta):

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
