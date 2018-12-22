import json
import os

from . import logger


def load(cfg_dir, cfg_file, default_cfg):
    """
    @param      cfg_dir  The directory to contain the config file
    @param
    """
    cfg_path = os.path.join(cfg_dir, cfg_file)
    cfg = dict(default_cfg)  # Copy the defaults

    try:
        with open(cfg_path) as f:
            cfg.update(json.load(f))
    except FileNotFoundError:
        pass

    # Write back to the file
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=4)

    logger.info(f"Loaded config: {cfg}")
    return cfg
