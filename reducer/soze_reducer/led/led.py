from soze_reducer.core.color import BLACK
from soze_reducer.core.resource import ReducerResource
from .mode import LedMode


class Led(ReducerResource):

    _COLOR_KEY = "reducer:led_color"

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            name="LED",
            settings_key="led",
            sub_channel="a2r:led",
            pub_channel="r2d:led",
            mode_class=LedMode,
            **kwargs,
        )

    def set_color(self, color):
        # Push the new color to Redis
        self._redis.set(__class__._COLOR_KEY, bytes(color))
        self.publish()

    def off(self):
        self.set_color(BLACK)

    def _before_stop(self):
        self.off()

    def _get_default_values(self):
        return (BLACK,)

    def _get_values(self):
        return (self._mode.get_color(self._settings),)

    def _apply_values(self, color):
        self.set_color(color)
