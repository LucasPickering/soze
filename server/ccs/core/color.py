from collections import namedtuple

Color = namedtuple('Color', 'red green blue')

BLACK = Color(0, 0, 0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
WHITE = Color(255, 255, 255)


def unpack_color(data):
    if type(data) is list and len(data) == 3:
        return Color(*data)  # Data is in a list, unpack the list into a color tuple
    raise ValueError(f"Invalid format for color data: {data}")
