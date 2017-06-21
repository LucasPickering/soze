from color import Color


class LcdMode:

    def __init__(self, user_settings):
        self.user_settings = user_settings

    def get_color(self):
        return None

    def get_text(self):
        return None


class LcdModeOff(LcdMode):

    BLACK = Color(0, 0, 0)

    def __init__(self, user_settings):
        super(LcdModeOff, self).__init__(user_settings)

    def get_color(self):
        return self.BLACK

    def get_text(self):
        return ''


class LcdModeClock(LcdMode):

    def __init__(self, user_settings):
        super(LcdModeClock, self).__init__(user_settings)

    def get_color(self):
        return self.user_settings.lcd_color

    def get_text(self):
        return ''
