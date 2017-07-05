#!/usr/bin/env python3

import argparse
import time
from lcd import Lcd

# Each character box is 5x8, represented as 8 5-bit lines
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
    parser.add_argument('-i', '--size', type=int, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="The width and height of the LCD (in characters)")
    parser.add_argument('-p', '--splash', nargs='+',
                        help="The splash text for the LCD to display on startup")
    args = parser.parse_args()

    lcd = Lcd(args.serial)

    if args.size:
        width, height = args.size
        print("Setting size to {}x{}".format(width, height))
        lcd.set_size(width, height)

    if args.splash:
        if width and height:
            size = width * height  # Total size of the LCD
            splash = ' '.join(args.splash)[:size]  # Join the words with spaces and cut down to size
            print("Setting splash text to '{}'".format(splash))
            splash = splash.ljust(size)  # Pad with spaces to max length
            lcd.set_splash_text(splash)
        else:
            raise Exception("Must set width and height in order to set splash text")

    print("Adding custom characters")
    for index, char in CHARS.items():
        lcd.create_char(index, char)

    lcd.on()
    lcd.clear()

    lcd.set_text('Setup successful!')
    print('Setup successful!')
    time.sleep(2.0)
    lcd.off()
    lcd.stop()


if __name__ == '__main__':
    main()
