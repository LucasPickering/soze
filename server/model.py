from collections import namedtuple
from recordclass import recordclass

Color = namedtuple('Color', 'red green blue')
Settings = recordclass('Settings', 'lcd_color lcd_text')


class Model:

    def __init__(self):
        self.led_color = Color(0, 0, 0)
        self.lcd_color = Color(0, 0, 0)
        self.lcd_text = ''
