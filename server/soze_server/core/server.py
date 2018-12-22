from threading import Thread

from soze_core.component import SozeComponent

from . import api, settings
from .keepalive import Keepalive
from soze_server.led.led import Led
from soze_server.lcd.lcd import Lcd

CFG_FILE = "sozes.json"
DEFAULT_CFG = {
    "led": {"socket_addr": "/tmp/soze_led.sock"},
    "lcd": {"socket_addr": "/tmp/soze_lcd.sock", "width": 20, "height": 4},
    "keepalive": {"socket_addr": "/tmp/soze_keepalive.sock"},
}


class SozeServer(SozeComponent):
    def __init__(self, args, **kwargs):
        super().__init__(
            args, cfg_file=CFG_FILE, default_cfg=DEFAULT_CFG, **kwargs
        )
        settings.init(args.working_dir)

    def _init_resources(self, cfg):
        keepalive = Keepalive(**cfg["keepalive"])
        return [
            keepalive,
            Led(settings=settings, keepalive=keepalive, **cfg["led"]),
            Lcd(settings=settings, keepalive=keepalive, **cfg["lcd"]),
        ]

    def _get_extra_threads(self, cfg):
        return [
            Thread(target=api.app.run, daemon=True, kwargs={"host": "0.0.0.0"})
        ]


def main():
    s = SozeServer.from_cmd_args()
    s.run()
