from color import Color


class LedMode:

    def __init__(self, user_settings):
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
