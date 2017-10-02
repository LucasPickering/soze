import abc

from ccs.core.mode import Mode


class LcdMode(Mode):

    MODES = {}

    def get_color(self, settings):
        return settings.get('lcd.color')

    @abc.abstractmethod
    def get_text(self, settings):
        pass

    @classmethod
    def _get_modes(cls):
        return cls.MODES
