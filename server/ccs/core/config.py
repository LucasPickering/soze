import json
import os

from ccs import logger

CFG_FILE = 'config.json'
DEFAULT_CFG = {
    'keepalive_hosts': [],
    'keepalive_timeout': 10,
    # Please don't ask about the ordering that's just how I wired it
    'red_pin': 5,
    'green_pin': 3,
    'blue_pin': 7,
    'lcd_device': '/dev/ttyAMA0',
    'lcd_width': 20,
    'lcd_height': 4,
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
