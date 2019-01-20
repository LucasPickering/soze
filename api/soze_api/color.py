import re

from .error import SozeError


def _check(val):
    if not isinstance(val, int):
        raise SozeError(f"Value must be int, but was {type(val)}")
    if val < 0 or val > 255:
        raise SozeError(f"Value must be [0, 255], but was {val}")
    return val


class Color:

    # Matches a color hexcode, with optional # or 0x prefix (caseless)
    _HEXCODE_RGX = re.compile(r"^(?:#|0x)?([a-z0-9]{6})$", flags=re.IGNORECASE)

    def __init__(self, red, green, blue):
        self._r = _check(red)
        self._g = _check(green)
        self._b = _check(blue)

    @classmethod
    def from_hexcode(cls, hex_val):
        return cls(
            (hex_val >> 16) & 0xFF, (hex_val >> 8) & 0xFF, hex_val & 0xFF
        )

    @classmethod
    def unpack(cls, data):
        # Try to parse it as a string
        try:
            # String hexcode format
            m = __class__._HEXCODE_RGX.match(data)
            if m:
                # Parse the hex value to an int
                return cls.from_hexcode(int(m.group(1), 16))
            raise SozeError(f"Invalid string format for color data: {data!r}")
        except TypeError:
            pass  # Data isn't a string, fall through to the next case

        # If it's an int, treat it as a hexcode
        if isinstance(data, int):
            return cls.from_hexcode(data)

        # Try to treat it as an iterable
        try:
            # If the data is an iterable of length 3, this will work
            # If it's not an iterable, raises a TypeError
            # If it doesn't have 3 args, raises a ValueError
            r, g, b = data
            return cls(r, g, b)
        except (TypeError, ValueError):
            pass  # Not an iterable or wrong length, fall through to the error

        raise SozeError(f"Invalid format for color data: {data!r}")

    @property
    def red(self):
        return self._r

    @property
    def green(self):
        return self._g

    @property
    def blue(self):
        return self._b

    def to_html(self):
        return f"#{int(self):06x}"

    def __int__(self):
        return (self.red << 16) | (self.green << 8) | self.blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def __repr__(self):
        return f"<Color: {self}>"


BLACK = Color(0, 0, 0)
