import argparse
import logging
import os
import signal
from threading import Thread

from . import api, config, settings
from .keepalive import Keepalive
from ccs import logger
from ccs.led.led import Led
from ccs.lcd.lcd import Lcd


class CaseControlServer:
    def __init__(self, args):
        if args.debug:
            logger.setLevel(logging.DEBUG)

        # Init config and settings
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)
        cfg = config.load(args.working_dir)
        settings.init(args.working_dir)

        # Init keepalive handler. This pings a list of hosts periodically, and if they are all
        # down, we turn everything off.
        self._keepalive = Keepalive(**cfg['keepalive'])

        # Init the LED/LCD handlers
        self._resources = [
            self._keepalive,
            Led(keepalive=self._keepalive, **cfg['led']),
            Lcd(keepalive=self._keepalive, **cfg['lcd']),
        ]
        logger.debug("Initialized resources")

        # Add background threads to be run. One for each resource, then one for the API
        self._threads = [res.make_thread(settings) for res in self._resources]
        self._threads.append(Thread(target=api.app.run, daemon=True, kwargs={'host': '0.0.0.0'}))

        # Register exit handler
        signal.signal(signal.SIGTERM, lambda sig, frame: self.stop())

    def run(self):
        try:
            # Start the helper threads, then launch the REST API
            logger.debug("Starting threads...")
            for thread in self._threads:
                thread.start()
            logger.debug("Started threads, now starting Flask...")
            logger.debug("Started Flask")

            self._wait()  # Wait for something to die
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def _wait(self):
        # Wait for all non-daemon threads to die
        for thread in self._threads:
            if not thread.daemon:
                thread.join()

    def stop(self):
        # Stop, if this hasn't already been called once
        logger.info("Stopping...")
        for res in self._resources:
            res.stop_loop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('working_dir', nargs='?', default='.',
                        help="Directory to store settings, config, etc.")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()
