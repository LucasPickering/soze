import abc

MODES = {}


class LedMode(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def _get_color(self, settings):
        pass

    @staticmethod
    def get_mode_names():
        return set(MODES.keys())

    @staticmethod
    def get_color(settings):
        """
        @brief      Gets the current color for the LEDs.

        @param      settings  The current settings

        @return     The current LED color, based on mode and other relevant settings.

        @raise      ValueError if the given LED mode is unknown
        """
        mode = MODES[settings.get('led.mode')]  # Get the relevant mode object
        return mode._get_color(settings)
