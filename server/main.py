#!/usr/bin/python3

import argparse
import threading
from lcd import Lcd


class Main:

    def __init__(self, args):
        self.run = True
        self.lcd = Lcd(args.serial)
        self.lcd.set_autoscroll(False)
        self.lcd.on()
        self.lcd.clear()
        self.lcd_thread = threading.Thread(target=self.lcd_thread)

    def start(self):
        self.socket_thread.start()
        self.lcd_thread.start()

    def stop(self):
        self.run = False

    def case_thread(self):
        # TODO periodically update case LEDs
        pass

    def lcd_thread(self):
        # TODO periodically update LCD
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--udp', type=int, default=5555,
                        help="UDP port to receive settings on")
    parser.add_argument('-s', '--serial', default='/dev/ttyAMA0',
                        help="Serial port to communicate with the LCD on")
    args = parser.parse_args()

    main = Main(args)
    main.start()


if __name__ == '__main__':
    main()
