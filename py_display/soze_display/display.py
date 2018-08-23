from soze_core.component import SozeComponent

from .led import Led
from .lcd import Lcd
from .keepalive import Keepalive

CFG_FILE = 'sozed.json'
DEFAULT_CFG = {
    'led': {
        'socket_addr': '/tmp/soze_led.sock',
        'hat_addr': 0x60,
        'pins': [3, 1, 2],  # RGB
    },
    'lcd': {
        'socket_addr': '/tmp/soze_lcd.sock',
        'serial_port': '/dev/ttyAMA0',
    },
    'keepalive': {
        'socket_addr': '/tmp/soze_keepalive.sock',
        'pin': 4,
    },
}


class SozeDisplay(SozeComponent):
    def __init__(self, args, **kwargs):
        super().__init__(args, cfg_file=CFG_FILE, default_cfg=DEFAULT_CFG, **kwargs)

    def _init_resources(self, cfg):
        return [
            Led(**cfg['led']),
            Lcd(**cfg['lcd']),
            Keepalive(**cfg['keepalive']),
        ]


def main():
    c = SozeDisplay.from_cmd_args()
    c.run()
