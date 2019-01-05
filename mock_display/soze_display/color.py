from xtermcolor import XTermColorMap


def _check(val):
    if not isinstance(val, int):
        raise TypeError(f"Value must be int, but was {type(val)}")
    if val < 0 or val > 255:
        raise ValueError(f"Value must be [0, 255], but was {val}")
    return val


xterm_color_map = XTermColorMap()


class Color:
    def __init__(self, red, green, blue):
        self._r = _check(red)
        self._g = _check(green)
        self._b = _check(blue)

    @classmethod
    def from_bytes(cls, b):
        return cls(*b[:3])  # Pass the first 3 bytes to the constructor

    @property
    def red(self):
        return self._r

    @property
    def green(self):
        return self._g

    @property
    def blue(self):
        return self._b

    def to_hexcode(self):
        return (self.red << 16) | (self.green << 8) | self.blue

    def to_term_color(self):
        ansi, _ = xterm_color_map.convert(self.to_hexcode())
        return ansi

    def __bytes__(self):
        return bytes([self.red, self.green, self.blue])

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def __repr__(self):
        return f"<Color: {str(self)}>"


BLACK = Color(0, 0, 0)
