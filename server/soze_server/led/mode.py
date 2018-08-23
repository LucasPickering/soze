import abc

from soze_server.core.mode import Mode


class LedMode(Mode):

    MODES = {}

    @abc.abstractmethod
    def get_color(self, settings):
        pass

    @classmethod
    def _get_modes(cls):
        return cls.MODES

    def __str__(self):
        return f"LED/{self.name}"
