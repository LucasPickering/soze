from threading import Thread

from cc_core.cce import CaseControlElement

from . import api, settings
from .keepalive import Keepalive
from ccs.led.led import Led
from ccs.lcd.lcd import Lcd

CFG_FILE = 'ccs.json'
DEFAULT_CFG = {
    'led': {
        'socket_addr': '/tmp/cc_led.sock',
    },
    'lcd': {
        'socket_addr': '/tmp/cc_lcd.sock',
        'width': 20,
        'height': 4,
    },
    'keepalive': {
        'socket_addr': '/tmp/cc_keepalive.sock',
    },
}


class CaseControlServer(CaseControlElement):
    def __init__(self, args, **kwargs):
        super().__init__(args, cfg_file=CFG_FILE, default_cfg=DEFAULT_CFG, **kwargs)
        settings.init(args.working_dir)

    def _init_resources(self, cfg):
        keepalive = Keepalive(**cfg['keepalive'])
        return [
            keepalive,
            Led(settings=settings, keepalive=keepalive, **cfg['led']),
            Lcd(settings=settings, keepalive=keepalive, **cfg['lcd']),
        ]

    def _get_extra_threads(self, cfg):
        return [Thread(target=api.app.run, daemon=True, kwargs={'host': '0.0.0.0'})]


def main():
    c = CaseControlServer.from_cmd_args()
    c.run()
