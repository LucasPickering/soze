import re


def coerce(val):
    return min(max(int(val), 0), 255)


class Color:
    # Used to convert RGB colors to xterm-256 colors
    # I recommend minimizing this if your editor has such a functionality
    # If it doesn't, stop using a garbage editor and switch to Sublime
    _RGB_TO_TERM = {  # color look-up table
        # Primary 3-bit (8 colors). Unique representation!
        0x000000: 0,
        0x800000: 1,
        0x008000: 2,
        0x808000: 3,
        0x000080: 4,
        0x800080: 5,
        0x008080: 6,
        0xC0C0C0: 7,
        # Equivalent "bright" versions of original 8 colors.
        0x808080: 8,
        0xFF0000: 9,
        0x00FF00: 10,
        0xFFFF00: 11,
        0x0000FF: 12,
        0xFF00FF: 13,
        0x00FFFF: 14,
        0xFFFFFF: 15,
        # Strictly ascending.
        0x000000: 16,
        0x00005F: 17,
        0x000087: 18,
        0x0000AF: 19,
        0x0000D7: 20,
        0x0000FF: 21,
        0x005F00: 22,
        0x005F5F: 23,
        0x005F87: 24,
        0x005FAF: 25,
        0x005FD7: 26,
        0x005FFF: 27,
        0x008700: 28,
        0x00875F: 29,
        0x008787: 30,
        0x0087AF: 31,
        0x0087D7: 32,
        0x0087FF: 33,
        0x00AF00: 34,
        0x00AF5F: 35,
        0x00AF87: 36,
        0x00AFAF: 37,
        0x00AFD7: 38,
        0x00AFFF: 39,
        0x00D700: 40,
        0x00D75F: 41,
        0x00D787: 42,
        0x00D7AF: 43,
        0x00D7D7: 44,
        0x00D7FF: 45,
        0x00FF00: 46,
        0x00FF5F: 47,
        0x00FF87: 48,
        0x00FFAF: 49,
        0x00FFD7: 50,
        0x00FFFF: 51,
        0x5F0000: 52,
        0x5F005F: 53,
        0x5F0087: 54,
        0x5F00AF: 55,
        0x5F00D7: 56,
        0x5F00FF: 57,
        0x5F5F00: 58,
        0x5F5F5F: 59,
        0x5F5F87: 60,
        0x5F5FAF: 61,
        0x5F5FD7: 62,
        0x5F5FFF: 63,
        0x5F8700: 64,
        0x5F875F: 65,
        0x5F8787: 66,
        0x5F87AF: 67,
        0x5F87D7: 68,
        0x5F87FF: 69,
        0x5FAF00: 70,
        0x5FAF5F: 71,
        0x5FAF87: 72,
        0x5FAFAF: 73,
        0x5FAFD7: 74,
        0x5FAFFF: 75,
        0x5FD700: 76,
        0x5FD75F: 77,
        0x5FD787: 78,
        0x5FD7AF: 79,
        0x5FD7D7: 80,
        0x5FD7FF: 81,
        0x5FFF00: 82,
        0x5FFF5F: 83,
        0x5FFF87: 84,
        0x5FFFAF: 85,
        0x5FFFD7: 86,
        0x5FFFFF: 87,
        0x870000: 88,
        0x87005F: 89,
        0x870087: 90,
        0x8700AF: 91,
        0x8700D7: 92,
        0x8700FF: 93,
        0x875F00: 94,
        0x875F5F: 95,
        0x875F87: 96,
        0x875FAF: 97,
        0x875FD7: 98,
        0x875FFF: 99,
        0x878700: 100,
        0x87875F: 101,
        0x878787: 102,
        0x8787AF: 103,
        0x8787D7: 104,
        0x8787FF: 105,
        0x87AF00: 106,
        0x87AF5F: 107,
        0x87AF87: 108,
        0x87AFAF: 109,
        0x87AFD7: 110,
        0x87AFFF: 111,
        0x87D700: 112,
        0x87D75F: 113,
        0x87D787: 114,
        0x87D7AF: 115,
        0x87D7D7: 116,
        0x87D7FF: 117,
        0x87FF00: 118,
        0x87FF5F: 119,
        0x87FF87: 120,
        0x87FFAF: 121,
        0x87FFD7: 122,
        0x87FFFF: 123,
        0xAF0000: 124,
        0xAF005F: 125,
        0xAF0087: 126,
        0xAF00AF: 127,
        0xAF00D7: 128,
        0xAF00FF: 129,
        0xAF5F00: 130,
        0xAF5F5F: 131,
        0xAF5F87: 132,
        0xAF5FAF: 133,
        0xAF5FD7: 134,
        0xAF5FFF: 135,
        0xAF8700: 136,
        0xAF875F: 137,
        0xAF8787: 138,
        0xAF87AF: 139,
        0xAF87D7: 140,
        0xAF87FF: 141,
        0xAFAF00: 142,
        0xAFAF5F: 143,
        0xAFAF87: 144,
        0xAFAFAF: 145,
        0xAFAFD7: 146,
        0xAFAFFF: 147,
        0xAFD700: 148,
        0xAFD75F: 149,
        0xAFD787: 150,
        0xAFD7AF: 151,
        0xAFD7D7: 152,
        0xAFD7FF: 153,
        0xAFFF00: 154,
        0xAFFF5F: 155,
        0xAFFF87: 156,
        0xAFFFAF: 157,
        0xAFFFD7: 158,
        0xAFFFFF: 159,
        0xD70000: 160,
        0xD7005F: 161,
        0xD70087: 162,
        0xD700AF: 163,
        0xD700D7: 164,
        0xD700FF: 165,
        0xD75F00: 166,
        0xD75F5F: 167,
        0xD75F87: 168,
        0xD75FAF: 169,
        0xD75FD7: 170,
        0xD75FFF: 171,
        0xD78700: 172,
        0xD7875F: 173,
        0xD78787: 174,
        0xD787AF: 175,
        0xD787D7: 176,
        0xD787FF: 177,
        0xD7AF00: 178,
        0xD7AF5F: 179,
        0xD7AF87: 180,
        0xD7AFAF: 181,
        0xD7AFD7: 182,
        0xD7AFFF: 183,
        0xD7D700: 184,
        0xD7D75F: 185,
        0xD7D787: 186,
        0xD7D7AF: 187,
        0xD7D7D7: 188,
        0xD7D7FF: 189,
        0xD7FF00: 190,
        0xD7FF5F: 191,
        0xD7FF87: 192,
        0xD7FFAF: 193,
        0xD7FFD7: 194,
        0xD7FFFF: 195,
        0xFF0000: 196,
        0xFF005F: 197,
        0xFF0087: 198,
        0xFF00AF: 199,
        0xFF00D7: 200,
        0xFF00FF: 201,
        0xFF5F00: 202,
        0xFF5F5F: 203,
        0xFF5F87: 204,
        0xFF5FAF: 205,
        0xFF5FD7: 206,
        0xFF5FFF: 207,
        0xFF8700: 208,
        0xFF875F: 209,
        0xFF8787: 210,
        0xFF87AF: 211,
        0xFF87D7: 212,
        0xFF87FF: 213,
        0xFFAF00: 214,
        0xFFAF5F: 215,
        0xFFAF87: 216,
        0xFFAFAF: 217,
        0xFFAFD7: 218,
        0xFFAFFF: 219,
        0xFFD700: 220,
        0xFFD75F: 221,
        0xFFD787: 222,
        0xFFD7AF: 223,
        0xFFD7D7: 224,
        0xFFD7FF: 225,
        0xFFFF00: 226,
        0xFFFF5F: 227,
        0xFFFF87: 228,
        0xFFFFAF: 229,
        0xFFFFD7: 230,
        0xFFFFFF: 231,
        # Gray-scale range.
        0x080808: 232,
        0x121212: 233,
        0x1C1C1C: 234,
        0x262626: 235,
        0x303030: 236,
        0x3A3A3A: 237,
        0x444444: 238,
        0x4E4E4E: 239,
        0x585858: 240,
        0x626262: 241,
        0x6C6C6C: 242,
        0x767676: 243,
        0x808080: 244,
        0x8A8A8A: 245,
        0x949494: 246,
        0x9E9E9E: 247,
        0xA8A8A8: 248,
        0xB2B2B2: 249,
        0xBCBCBC: 250,
        0xC6C6C6: 251,
        0xD0D0D0: 252,
        0xDADADA: 253,
        0xE4E4E4: 254,
        0xEEEEEE: 255,
    }

    def __init__(self, red, green, blue):
        self._r = Color._check(red)
        self._g = Color._check(green)
        self._b = Color._check(blue)

    @staticmethod
    def _check(val):
        if not isinstance(val, int):
            raise TypeError(f"Value must be int, but was {type(val)}")
        if val < 0 or val > 255:
            raise ValueError(f"Value must be [0, 255], but was {val}")
        return val

    @classmethod
    def from_hexcode(cls, hex_val):
        return cls(
            (hex_val >> 16) & 0xFF, (hex_val >> 8) & 0xFF, hex_val & 0xFF
        )

    @classmethod
    def from_bytes(cls, b):
        return cls(*b[:3])  # Pass the first 3 bytes to the constructor

    @classmethod
    def unpack(cls, data):
        if isinstance(data, str):
            m = re.match(
                r"^(?:#|0x)?([A-Za-z0-9]{6})$", data
            )  # Parse hexcode format
            if m:
                return cls.from_hexcode(int(m.group(1), 16))
            # Match failed, fall through to error
        elif isinstance(data, int):
            return cls.from_hexcode(data)
        elif (isinstance(data, list) or isinstance(data, tuple)) and len(
            data
        ) == 3:
            return cls(
                *data
            )  # Data is in a list, unpack the list into a color tuple
        raise ValueError(f"Invalid format for color data: {data!r}")

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

    def to_hex_str(self):
        return f"0x{self.to_hexcode():06x}"

    def to_list(self):
        return [self.red, self.green, self.blue]

    def to_term_color(self):
        hexcode = self.to_hexcode()

        # Yes this is O(n) and yes this could be O(logn) but go fuck yourself
        closest_hex = min(
            Color._RGB_TO_TERM.keys(), key=lambda x: abs(x - hexcode)
        )
        return Color._RGB_TO_TERM[closest_hex]

    def __bytes__(self):
        return bytes(self.to_list())

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def __repr__(self):
        s = str(self)
        return f"<Color: {s}>"

    def __add__(self, other):
        if not isinstance(other, Color):
            raise TypeError(
                "unsupported operand type(s) for +:"
                f" '{type(self)}' and '{type(other)}'"
            )
        r = coerce(self.red + other.red)
        g = coerce(self.green + other.green)
        b = coerce(self.blue + other.blue)
        return Color(r, g, b)

    def __sub__(self, other):
        if not isinstance(other, Color):
            raise TypeError(
                "unsupported operand type(s) for -:"
                f" '{type(self)}' and '{type(other)}'"
            )
        r = coerce(self.red - other.red)
        g = coerce(self.green - other.green)
        b = coerce(self.blue - other.blue)
        return Color(r, g, b)

    def __mul__(self, coeff):
        if not isinstance(coeff, int) and not isinstance(coeff, float):
            raise TypeError(
                "unsupported operand type(s) for *:"
                f" '{type(self)}' and '{type(coeff)}'"
            )
        r = coerce(self.red * coeff)
        g = coerce(self.green * coeff)
        b = coerce(self.blue * coeff)
        return Color(r, g, b)

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

    def default(self):
        # Convert to JSON
        return [self.red, self.green, self.blue]


BLACK = Color(0, 0, 0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
WHITE = Color(255, 255, 255)
