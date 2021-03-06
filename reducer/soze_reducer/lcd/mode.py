import abc

from soze_reducer.core.color import BLACK, Color
from soze_reducer.core.mode import Mode


class LcdMode(Mode):

    MODES = {}

    def get_color(self, settings):
        try:
            return Color.from_hexcode(settings["color"])
        except KeyError:
            return BLACK

    @abc.abstractmethod
    def get_text(self, settings):
        pass

    @classmethod
    def _get_modes(cls):
        return cls.MODES

    def __str__(self):
        return f"LCD/{self.name}"
