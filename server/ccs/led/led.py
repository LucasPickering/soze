import traceback

from ccs import logger
from ccs.core.color import BLACK
from ccs.core.socket_resource import SettingsResource


class Led(SettingsResource):
    @property
    def name(self):
        return 'LED'

    def set_color(self, color):
        self._send(bytes(color))

    def off(self):
        self.set_color(BLACK)

    def cleanup(self):
        try:
            self.off()
        except Exception:
            logger.error("Error turning off LEDs:\n{}".format(traceback.format_exc()))

    def _get_default_values(self, settings):
        return (BLACK,)

    def _get_values(self, settings):
        return (settings.get('led.mode').get_color(settings),)

    def _apply_values(self, color):
        self.set_color(color)
