import abc

from ccs.core.named import Named


class LedMode(Named, metaclass=abc.ABCMeta):

    MODES = {}

    @abc.abstractmethod
    def get_color(self, settings):
        pass

    @staticmethod
    def get_mode_names():
        return set(LedMode.MODES.keys())

    @staticmethod
    def get_by_name(name):
        return LedMode.MODES[name]
