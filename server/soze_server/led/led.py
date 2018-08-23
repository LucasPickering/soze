from soze_server.core.color import BLACK
from soze_server.core.settings_resource import SettingsResource


class Led(SettingsResource):
    @property
    def name(self):
        return 'LED'

    def set_color(self, color):
        self._write(bytes(color))

    def off(self):
        self.set_color(BLACK)

    def _before_close(self):
        self.off()

    def _get_default_values(self):
        return (BLACK,)

    def _get_values(self):
        return (self._settings.get('led.mode').get_color(self._settings),)

    def _apply_values(self, color):
        self.set_color(color)
