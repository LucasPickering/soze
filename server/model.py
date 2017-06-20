from collections import namedtuple
from recordclass import recordclass

Color = namedtuple('Color', 'red green blue')
Settings = recordclass('Settings', 'led_color lcd_color lcd_text')
