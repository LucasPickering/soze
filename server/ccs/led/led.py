import traceback

from ccs import logger
from ccs.core.color import BLACK
from ccs.core.socket_resource import SocketResource


class Led(SocketResource):
    def set_color(self, color):
        self.send(bytes(color))

    def stop(self):
        try:
            self.off()
        except Exception:
            logger.error("Error turning off LEDs:\n{}".format(traceback.format_exc()))
        finally:
            self.close()

    def off(self):
        self.set_color(BLACK)
