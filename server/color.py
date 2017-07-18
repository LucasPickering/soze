from collections import namedtuple

Color = namedtuple('Color', 'red green blue')


def unpack_color(data):
    if type(data) is list and len(data) == 3:
        return Color(*data)  # Data is in a list, unpack the list into a color tuple
    raise ValueError("Invalid format for color data: {}".format(data))
