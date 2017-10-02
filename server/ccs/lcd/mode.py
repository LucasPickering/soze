import abc

from ccs.core.named import Named


class LcdMode(Named, metaclass=abc.ABCMeta):

    MODES = {}

    def get_color(self, settings):
        return settings.get('lcd.color')

    @abc.abstractmethod
    def get_text(self, settings):
        pass

    @staticmethod
    def get_mode_names():
        return set(LcdMode.MODES.keys())

    @staticmethod
    def get_by_name(name):
        return LcdMode.MODES[name]
