from color import Color

_BLACK = Color(0, 0, 0)


class LedMode:

    def __init__(self, config, user_settings, mode_name):
        self.config = config
        self.user_settings = user_settings

    def get_color(self):
        return None


class LedModeOff(LedMode):

    NAME = 'off'

    def get_name(self):
        return 'off'

    def get_color(self):
        return _BLACK


class LedModeStatic(LedMode):

    NAME = 'static'

    def get_color(self):
        return self.user_settings.led_static_color


_classes = [LedModeOff, LedModeStatic]
_names = {cls.NAME: cls for cls in _classes}


def get_by_name(name, config, user_settings):
    try:
        return _names[name](config, user_settings, name)
    except KeyError:
        raise ValueError("Invalid name: {}. Valid names are: {}".format(name, list(_names.keys())))
