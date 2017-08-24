import configparser

from .. import logger
from .singleton import Singleton

_DEFAULT_CFG_FILE = 'default.ini'


class Config(metaclass=Singleton):

    def init(self, cfg_file):
        # This is separate from the constructor so that anyone can use get this instance via the
        # constructor without having to initialize the class

        # Read config values from default file, then user file
        config = configparser.SafeConfigParser()
        config.read(_DEFAULT_CFG_FILE)
        config.read(cfg_file)

        # Print loaded values
        cfg_dict = {sct: dict(config.items(sct)) for sct in config.sections()}
        logger.info(f"Loaded config: {cfg_dict}")

        # Load values
        self.keepalive_host = config.get('main', 'keepalive_host')
        self.lcd_serial_device = config.get('lcd', 'serial_device')
        self.lcd_width = config.getint('lcd', 'width')
        self.lcd_height = config.getint('lcd', 'height')

        # Save the config back to the file
        with open(cfg_file, 'w') as f:
            config.write(f)
