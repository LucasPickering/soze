import abc
import argparse
import logging
import os
import signal

from . import config, logger


class CaseControlElement:
    def __init__(self, args, cfg_file, default_cfg):
        # Change logging level if debug flag is set
        if args.debug:
            logger.setLevel(logging.DEBUG)

        # Init config
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)
        cfg = config.load(args.working_dir, cfg_file, default_cfg)

        # Init the resource handlers
        self._resources = self._init_resources(cfg)
        logger.debug("Initialized resources")

        self._threads = self._resources + self._get_extra_threads(cfg)

        # Register exit handlers
        def stop_handler(sig, frame):
            self.stop()
        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)

    @classmethod
    def from_cmd_args(cls, *args, **kwargs):
        parser = argparse.ArgumentParser()
        parser.add_argument('working_dir', nargs='?', default='.',
                            help="Directory to store settings, config, etc.")
        parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
        cmd_args = parser.parse_args()

        return cls(*args, args=cmd_args, **kwargs)

    @abc.abstractmethod
    def _init_resources(self, cfg):
        pass

    def _get_extra_threads(self, cfg):
        return []

    def run(self):
        # Start the helper threads
        logger.debug("Starting threads...")
        for thread in self._threads:
            thread.start()
        logger.debug("Started threads")

        self._wait()

    def _wait(self):
        # Wait for all non-daemon threads to die
        for thread in self._threads:
            if not thread.daemon:
                thread.join()

    def stop(self):
        for res in self._resources:
            res.stop()
