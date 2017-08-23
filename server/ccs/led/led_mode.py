from ccs.core.color import BLACK


class LedMode:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def get_color(self):
        return None


class LedModeOff(LedMode):

    NAME = 'off'

    def get_name(self):
        return 'off'

    def get_color(self):
        return BLACK


class LedModeStatic(LedMode):

    NAME = 'static'

    def get_color(self):
        from ccs.core import user_settings  # Workaround!!
        return user_settings.led_static_color


_classes = [LedModeOff, LedModeStatic]
_names = {cls.NAME: cls for cls in _classes}


def get_by_name(name):
    try:
        return _names[name](name)
    except KeyError:
        valid_names = list(_names.keys())
        raise ValueError(f"Invalid name: {name}. Valid names are: {valid_names}")
