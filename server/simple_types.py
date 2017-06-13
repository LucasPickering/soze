from collections import namedtuple
from recordclass import recordclass

Color = namedtuple('Color', 'red green blue')
Settings = recordclass('Settings', 'lcd_text lcd_color')
