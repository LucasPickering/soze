from soze_reducer.core.color import BLACK
from soze_reducer.core.resource import ReducerResource
from soze_reducer.led.mode import LedMode


class Led(ReducerResource):

    _MODE_KEY = "led:mode"
    _COLOR_KEY = "reducer:led_color"

    @property
    def name(self):
        return "LED"

    @property
    def settings_key_prefix(self):
        return "led"

    @property
    def sub_channel(self):
        return "a2r:led"

    @property
    def pub_channel(self):
        return "r2d:led"

    def set_color(self, color):
        self._redis.set(__class__._COLOR_KEY, bytes(color))

    def off(self):
        self.set_color(BLACK)

    def _after_reload(self):
        # If the mode changed, re-initialize it
        new_mode = self._settings[__class__._MODE_KEY]
        if new_mode != self._mode.name:
            self._mode = LedMode.get_by_name(new_mode)

    def _before_close(self):
        self.off()

    def _get_default_values(self):
        return (BLACK,)

    def _get_values(self):
        return (self._mode.get_color(self._settings),)

    def _apply_values(self, color):
        self.set_color(color)
        return True
