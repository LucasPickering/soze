import itertools
from collections import defaultdict
from enum import Enum

# Custom chars (e.g. the small blocks used to make big chars) are defined here
# Each character box is 5x8, represented as 8 5-bit lines
CUSTOM_CHARS = {
    0x00: [
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00011,
        0b01111,
        0b01111,
        0b11111,
    ],
    0x01: [
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b11000,
        0b11110,
        0b11110,
        0b11111,
    ],
    0x02: [
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
    ],
    0x03: [
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b01111,
        0b01111,
        0b00011,
    ],
    0x04: [
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11110,
        0b11110,
        0b11000,
    ],
}

# Aliases for the small characters used to make big characters
HBR = "\x00"  # Half-bottom right
HBL = "\x01"  # Half-bottom left
BOT = "\x02"  # Half-bottom
FBR = "\x03"  # Full-bottom right
FBL = "\x04"  # Full-bottom left
FUL = "\xff"  # Full rectangle
EMT = " "  # Empty (space)

# Character arrays for big characters
BIG_CHARS = {
    "0": [HBR + BOT + HBL, FUL + EMT + FUL, FBR + BOT + FBL],
    "1": [BOT + HBL + EMT, EMT + FUL + EMT, BOT + FUL + BOT],
    "2": [HBR + BOT + HBL, HBR + BOT + FBL, FBR + BOT + BOT],
    "3": [HBR + BOT + HBL, EMT + BOT + FUL, BOT + BOT + FBL],
    "4": [BOT + EMT + BOT, FBR + BOT + FUL, EMT + EMT + FUL],
    "5": [BOT + BOT + BOT, FUL + BOT + HBL, BOT + BOT + FBL],
    "6": [HBR + BOT + HBL, FUL + BOT + HBL, FBR + BOT + FBL],
    "7": [BOT + BOT + BOT, EMT + HBR + FBL, EMT + FUL + EMT],
    "8": [HBR + BOT + HBL, FUL + BOT + FUL, FBR + BOT + FBL],
    "9": [HBR + BOT + HBL, FBR + BOT + FUL, EMT + EMT + FUL],
    ":": [FUL, EMT, FUL],
    " ": [EMT + EMT + EMT, EMT + EMT + EMT, EMT + EMT + EMT],
}

# Special signals for the controller
SIG_COMMAND = 0xFE
CMD_CLEAR = 0x58
CMD_BACKLIGHT_ON = 0x42
CMD_BACKLIGHT_OFF = 0x46
CMD_SIZE = 0xD1
CMD_SPLASH_TEXT = 0x40
CMD_BRIGHTNESS = 0x98
CMD_CONTRAST = 0x91
CMD_COLOR = 0xD0
CMD_AUTOSCROLL_ON = 0x51
CMD_AUTOSCROLL_OFF = 0x52
CMD_UNDERLINE_CURSOR_ON = 0x4A
CMD_UNDERLINE_CURSOR_OFF = 0x4B
CMD_BLOCK_CURSOR_ON = 0x53
CMD_BLOCK_CURSOR_OFF = 0x54
CMD_CURSOR_HOME = 0x48
CMD_CURSOR_POS = 0x47
CMD_CURSOR_FWD = 0x4D
CMD_CURSOR_BACK = 0x4C
CMD_CREATE_CHAR = 0x4E
CMD_SAVE_CUSTOM_CHAR = 0xC1
CMD_LOAD_CHAR_BANK = 0xC0


class CursorMode(Enum):
    off = 1
    underline = 2
    block = 3


def make_big_text(text):
    """
    @brief      Converts the given string into "big text". Big text is is three
                lines high.

    @param      text  The text to make big

    @return     The big text, as a list of 3 strings, one for each line
    """
    big_chars = (BIG_CHARS[c] for c in text)
    line_tuples = zip(*big_chars)
    return (" ".join(t) for t in line_tuples)  # Put a space between characters


def diff_text(lines1, lines2):
    """
    @brief      Diffs the given lists of strings, producing a dict of (x,y):str
                tuples of the text from lines2 where they differed. Adjacent
                differing characters are included together in the same string.
                If one list is longer then the other, the shorter list is padded
                with empty strings. If one line is longer than its counterpart,
                the shorter string is padded with spaces. See unit tests for
                examples.

    @param      lines1  The first list of strings
    @param      lines2  The second list of strings (this one takes priority)

    @return     A dict of (x,y):str tuples representing the changes
    """
    diff = defaultdict(
        lambda: []
    )  # List of chars is more efficient for building up
    for y, (line1, line2) in enumerate(
        itertools.zip_longest(lines1, lines2, fillvalue="")
    ):
        pos = None
        for x, (c1, c2) in enumerate(
            itertools.zip_longest(line1, line2, fillvalue=" ")
        ):
            if c1 != c2:
                if pos is None:
                    pos = (x, y)
                diff[pos].append(c2)
            else:
                pos = None
    return {k: "".join(v) for k, v in diff.items()}
