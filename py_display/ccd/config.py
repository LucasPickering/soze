import json
import os

from . import logger

CFG_FILE = 'ccd.json'
DEFAULT_CFG = {
    'led': {
        'socket': '/tmp/cc_led.sock',
        'hat_addr': 0x60,
        'pins': [3, 1, 2],  # RGB
    },
    'lcd': {
        'socket': '/tmp/cc_lcd.sock',
        'serial_port': '/dev/ttyAMA0',
    },
    'keepalive': {
        'socket': '/tmp/cc_keepalive.sock',
        'pin': 4,
    },
}


def load(settings_dir):
    """
    @param      settings_dir  The directory to contain the config file
    """
    cfg_file = os.path.join(settings_dir, CFG_FILE)
    cfg = dict(DEFAULT_CFG)  # Copy the defaults

    try:
        with open(cfg_file) as f:
            cfg.update(json.load(f))
    except FileNotFoundError:
        pass

    # Write back to the file
    with open(cfg_file, 'w') as f:
        json.dump(cfg, f, indent=4)

    logger.info(f"Loaded config: {cfg}")
    return cfg
