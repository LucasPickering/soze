import argparse
import logging
import os
import time
import traceback

from . import config, logger
from .led import Led
from .lcd import Lcd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('working_dir', nargs='?', default='.',
                        help="Directory to store settings, config, etc.")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    # Change logging level if debug flag is set
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Init config
    if not os.path.exists(args.working_dir):
        os.makedirs(args.working_dir)
    cfg = config.load(args.working_dir)

    resources = [
        Led(cfg['led']['socket'],
            cfg['led']['red_pin'], cfg['led']['green_pin'], cfg['led']['blue_pin']),
        Lcd(cfg['lcd']['socket'], cfg['lcd']['serial_port']),
    ]

    try:
        # Start each resource
        for res in resources:
            res.start()

        # Wait for Ctrl-c
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.error(traceback.format_exc())
    finally:
        for res in resources:
            res.close()
