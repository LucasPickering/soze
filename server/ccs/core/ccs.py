import argparse
import logging
import os
import signal
import subprocess
import time
from threading import Thread

from . import api, config, settings
from ccs import logger
from ccs.led.led import Led
from ccs.lcd.lcd import Lcd

KEEPALIVE_THREAD_PAUSE = 1.0


class CaseControlServer:
    def __init__(self, args):
        self._keepalive_up = True

        if args.debug:
            logger.setLevel(logging.DEBUG)

        # Init config and settings
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)
        cfg = config.load(args.working_dir)
        settings.init(args.working_dir)

        # Init the LED/LCD handlers
        self._resources = [
            Led(cfg['led']['socket']),
            Lcd(cfg['lcd']['socket'], cfg['lcd']['width'], cfg['lcd']['height']),
        ]
        logger.debug("Initialized resources")

        keepalive_hosts = cfg['keepalive']['hosts']
        keepalive_timeout = cfg['keepalive']['timeout']

        # Add background threads to be run
        self._threads = [res.make_thread(settings) for res in self._resources] + [
            Thread(target=self._keepalive_thread, name='Keepalive-Thread', daemon=True,
                   args=(keepalive_hosts, keepalive_timeout)),
            Thread(target=api.app.run, daemon=True, kwargs={'host': '0.0.0.0'}),
        ]

        signal.signal(signal.SIGTERM, lambda sig, frame: self.stop())  # Catch SIGTERM

    def run(self):
        # Start the helper threads, then launch the REST API
        try:
            logger.debug("Starting threads...")
            for thread in self._threads:
                thread.start()
            logger.debug("Started threads, now starting Flask...")
            logger.debug("Started Flask")

            self._wait()  # Wait for something to die
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()  # Shut down every thread/process

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

    def _keepalive_thread(self, hosts, timeout):
        # No hosts given, don't even bother
        if not hosts:
            return

        def ping(host):
            try:
                subprocess.check_call(['ping', '-c', '1', '-W', str(timeout), host],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                return False
        try:
            while True:
                awake = any(ping(host) for host in hosts)  # If any hosts are alive...
                if awake != self._keepalive_up:
                    logger.info(f"Keepalive host(s) went {'up' if awake else 'down'}")
                    for res in self._resources:
                        res.awake = awake
                time.sleep(KEEPALIVE_THREAD_PAUSE)
        finally:
            self.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('working_dir', nargs='?', default='.',
                        help="Directory to store settings, config, etc.")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()
