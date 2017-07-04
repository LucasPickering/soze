#!/usr/bin/env python3

import argparse
from lcd import Lcd

HBR = [0b00000, 0b00000, 0b00000, 0b00000, 0b00011, 0b01111, 0b01111, 0b11111]
HBL = [0b00000, 0b00000, 0b00000, 0b00000, 0b11000, 0b11110, 0b11110, 0b11111]
BOT = [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111, 0b11111]
FBR = [0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b01111, 0b01111, 0b00011]
FBL = [0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11110, 0b11110, 0b11000]
CHARS = {
    0: HBR,
    1: HBL,
    2: BOT,
    3: FBR,
    4: FBL
}


def main():
    parser = argparse.ArgumentParser(description="First time setup for your LCD.")
    parser.add_argument('-s', '--serial', default='/dev/ttyAMA0',
                        help="Serial port to communicate with the LCD on")
    parser.add_argument('--width', required=True, type=int,
                        help="The width of the LCD (in characters)")
    parser.add_argument('--height', required=True, type=int,
                        help="The height of the LCD (in characters)")
    args = parser.parse_args()

    lcd = Lcd(args.serial)
    lcd.set_size(args.width, args.height)

    for index, char in CHARS.items():
        lcd.create_char(index, char)
    lcd.save_custom_chars()


if __name__ == '__main__':
    main()
