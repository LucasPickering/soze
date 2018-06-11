import abc

from cc_core.resource import WriteResource


class SettingsResource(WriteResource):
    def __init__(self, settings, keepalive, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settings = settings
        self._keepalive = keepalive

    def _update(self):
        # Calculate real values if the keepalive is alive, otherwise use default values
        values = self._get_values() if self._keepalive.is_alive else self._get_default_values()
        self._apply_values(*values)

    @abc.abstractmethod
    def _get_default_values(self):
        pass

    @abc.abstractmethod
    def _get_values(self):
        pass

    @abc.abstractmethod
    def _apply_values(self, *values):
        pass
