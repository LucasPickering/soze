#!/usr/bin/env python3
import argparse

from ccs.ccs import CaseControlServer

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('-c', '--config', default='config.ini', help="Specify the config file")
    parser.add_argument('-m', '--mock', action='store_const', default=False, const=True,
                        help="Mock the LEDs/LCD in the console for development")
    parser.add_argument('-n', '--null', action='store_const', default=False, const=True,
                        help="Don't output data at all (no hardware or mocking)")
    parser.add_argument('-s', '--settings', default='settings.json',
                        help="Specify the settings file that will be saved to and loaded from")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()
