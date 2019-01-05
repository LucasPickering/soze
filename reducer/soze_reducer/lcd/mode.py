import abc

from soze_reducer.core.color import BLACK, Color
from soze_reducer.core.mode import Mode


class LcdMode(Mode):

    MODES = {}
    _COLOR_KEY = "color"

    def get_color(self, settings):
        try:
            return Color.from_bytes(settings[__class__._COLOR_KEY])
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
