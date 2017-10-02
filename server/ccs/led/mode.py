import abc

from ccs.core.mode import Mode


class LedMode(Mode):

    MODES = {}

    @abc.abstractmethod
    def get_color(self, settings):
        pass

    @classmethod
    def _get_modes(cls):
        return cls.MODES
