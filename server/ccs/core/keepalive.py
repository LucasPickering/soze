import subprocess
import time
from threading import Thread

from ccs import logger


def ping(host, timeout):
    try:
        subprocess.check_call(['ping', '-c', '1', host], timeout=timeout,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


class Keepalive:

    def __init__(self, hosts, timeout):
        self._hosts = hosts
        self._timeout = timeout
        self._alive = True

    @property
    def is_alive(self):
        return self._alive

    def make_thread(self):
        return Thread(target=self._run, name='Keepalive-Thread', daemon=True)

    def _ping(self, host):
        try:
            subprocess.check_call(['ping', '-c', '1', host], timeout=self._timeout,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def _ping_all(self):
        """
        @brief      Ping all hosts. As soon as one ping is successful, return success. If no hosts
                    can be pinged, retry until time runs out. If time runs out and no successful
                    pings occurred, return failure. Failure will always take about as long as the
                    timeout value that this object was initialized with.

        @return     True for success, False for failure
        """

        start_time = time.time()  # For timeout purposes
        while time.time() - start_time < self._timeout:  # Retry until we run out of time
            for host in self._hosts:  # Ping each host
                elapsed_time = time.time() - start_time  # Time since we started pinging all hosts
                time_left = self._timeout - elapsed_time  # Calculate time remaining until timeout
                alive = ping(host, time_left)  # Ping host with timeout

                # Short circuit on success
                if alive:
                    return True
        return False

    def _run(self):
        # No hosts given, don't even bother
        if not self._hosts:
            return

        while True:
            alive = self._ping_all()  # If any hosts are alive...

            # If the value flipped, log it, then update our state
            if alive != self._alive:
                logger.info(f"Keepalive host(s) went {'up' if alive else 'down'}")
            self._alive = alive
