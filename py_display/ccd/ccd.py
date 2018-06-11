from cc_core.cce import CaseControlElement

from .led import Led
from .lcd import Lcd
from .keepalive import Keepalive

CFG_FILE = 'ccd.json'
DEFAULT_CFG = {
    'led': {
        'socket_addr': '/tmp/cc_led.sock',
        'hat_addr': 0x60,
        'pins': [3, 1, 2],  # RGB
    },
    'lcd': {
        'socket_addr': '/tmp/cc_lcd.sock',
        'serial_port': '/dev/ttyAMA0',
    },
    'keepalive': {
        'socket_addr': '/tmp/cc_keepalive.sock',
        'pin': 4,
    },
}


class CaseControlDisplay(CaseControlElement):
    def __init__(self, args, **kwargs):
        super().__init__(args, cfg_file=CFG_FILE, default_cfg=DEFAULT_CFG, **kwargs)

    def _init_resources(self, cfg):
        return [
            Led(**cfg['led']),
            Lcd(**cfg['lcd']),
            Keepalive(**cfg['keepalive']),
        ]


def main():
    c = CaseControlDisplay.from_cmd_args()
    c.run()
