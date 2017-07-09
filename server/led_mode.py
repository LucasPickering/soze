from color import Color


class LedMode:

    def __init__(self, config, user_settings):
        self.config = config
        self.user_settings = user_settings

    def get_color(self):
        return None


class LedModeOff(LedMode):

    BLACK = Color(0, 0, 0)

    def get_color(self):
        return self.BLACK


class LedModeStatic(LedMode):

    def get_color(self):
        return self.user_settings.led_static_color


_names = {
    'off': LedModeOff,
    'static': LedModeStatic
}


def get_by_name(name, config, user_settings):
    try:
        return _names[name](config, user_settings)
    except KeyError:
        raise ValueError("Invalid name: {}. Valid names are: {}".format(name, _names.keys()))
