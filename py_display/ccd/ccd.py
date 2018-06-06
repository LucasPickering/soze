import argparse
import logging
import os
import signal
import time

from . import config, logger
from .led import Led
from .lcd import Lcd
from .keepalive import Keepalive


class CaseControlDisplay:
    def __init__(self, args):
        # Change logging level if debug flag is set
        if args.debug:
            logger.setLevel(logging.DEBUG)

        # Init config
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)
        cfg = config.load(args.working_dir)

        # Init the resource handlers
        self._resources = [
            Led(**cfg['led']),
            Lcd(**cfg['lcd']),
            Keepalive(**cfg['keepalive']),
        ]
        logger.debug("Initialized resources")

        # Register exit handler
        signal.signal(signal.SIGTERM, lambda sig, frame: self.stop())

    def run(self):
        try:
            # Start each resource
            for res in self._resources:
                res.start()
            self._wait()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def _wait(self):
        # Wait for Ctrl-c
        while True:
            time.sleep(1000)

    def stop(self):
        # Stop, if this hasn't already been called once
        logger.info("Stopping...")
        for res in self._resources:
            res.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('working_dir', nargs='?', default='.',
                        help="Directory to store settings, config, etc.")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    c = CaseControlDisplay(args)
    c.run()
