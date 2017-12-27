import json
import os

from ccs import logger

CFG_FILE = 'ccs.json'
DEFAULT_CFG = {
    'led': {
        'socket': '/tmp/cc_led.sock',
    },
    'lcd': {
        'socket': '/tmp/cc_lcd.sock',
        'width': 20,
        'height': 4,
    },
    'keepalive': {
        'hosts': [],
        'timeout': 30,
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
