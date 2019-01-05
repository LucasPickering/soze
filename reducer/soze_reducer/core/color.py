def _coerce(r, g, b):
    def helper(val):
        return min(max(int(val), 0), 255)

    return (helper(r), helper(g), helper(b))


def _check(val):
    if not isinstance(val, int):
        raise TypeError(f"Value must be int, but was {type(val)}")
    if val < 0 or val > 255:
        raise ValueError(f"Value must be [0, 255], but was {val}")
    return val


class Color:
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

    def blend(self, other, bias=0.5):
        """
        @brief      Blend this color with another one.

        @param      self   The object
        @param      other  The other color to blend with
        @param      bias   The bias towards this color in the blend [0, 1]

        @return     The blended color, as a new Color object
        """
        if bias < 0 or 1 < bias:
            raise ValueError(f"Bias must be in range [0, 1], but was {bias}")
        other_bias = 1.0 - bias

        def mix(this, other):
            return int(this * bias + other * other_bias)

        return Color(
            mix(self.red, other.red),
            mix(self.green, other.green),
            mix(self.blue, other.blue),
        )

    def __bytes__(self):
        return bytes([self.red, self.green, self.blue])

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def __repr__(self):
        return f"<Color: {self}>"

    def __add__(self, other):
        if not isinstance(other, Color):
            raise TypeError(
                "unsupported operand type(s) for +:"
                f" '{type(self)}' and '{type(other)}'"
            )
        r, g, b = _coerce(
            self.red + other.red,
            self.green + other.green,
            self.blue + other.blue,
        )
        return Color(r, g, b)

    def __mul__(self, coeff):
        if not isinstance(coeff, int) and not isinstance(coeff, float):
            raise TypeError(
                "unsupported operand type(s) for *:"
                f" '{type(self)}' and '{type(coeff)}'"
            )
        r, g, b = _coerce(
            self.red * coeff, self.green * coeff, self.blue * coeff
        )
        return Color(r, g, b)


BLACK = Color(0, 0, 0)
