import os
from configparser import SafeConfigParser

from ccs import logger

CFG_FILE = 'ccs.ini'
DEFAULT_CFG = {
    'led': {
        # Please don't ask about the ordering that's just how I wired it
        'red_pin': 5,
        'green_pin': 3,
        'blue_pin': 7,
    },
    'lcd': {
        'device': '/dev/ttyAMA0',
        'width': 20,
        'height': 4,
    },
}


def load(settings_dir):
    """
    @param      settings_dir  The directory to contain the config file
    """
    config_file = os.path.join(settings_dir, CFG_FILE)
    cfg = SafeConfigParser()

    # Init default values
    for section, values in DEFAULT_CFG.items():
        cfg[section] = values
    cfg.read(config_file)  # Read the file

    # Write back to the file
    with open(config_file, 'w') as f:
        cfg.write(f)

    logger.info(f"Loaded config with sections {cfg.sections()}")
    for sect, opts in cfg.items():
        logger.debug(f"{sect}: {dict(opts)}")
    return cfg
