#!/usr/bin/env python3

import argparse

from ccs.ccs import CaseControlServer
from ccs.ccs.lcd.helper import DEFAULT_WIDTH, DEFAULT_HEIGHT

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    parser.add_argument('--lcd-serial', default='/dev/ttyAMA0', help="Serial device for the LCD")
    parser.add_argument('--lcd-width', type=int, default=DEFAULT_WIDTH,
                        help="LCD width, in characters")
    parser.add_argument('--lcd-height', type=int, default=DEFAULT_HEIGHT,
                        help="LCD height, in characters")
    parser.add_argument('--keepalive', default=None, help="Host to use for keepalive check")
    parser.add_argument('--mock', '-m', action='store_const', default=False, const=True,
                        help="Mock the LEDs/LCD in the console for development")
    parser.add_argument('--settings', '-s', default='settings.p',
                        help="Specify the settings file that will be saved to and loaded from")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()
