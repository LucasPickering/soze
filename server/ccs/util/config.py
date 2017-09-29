import os
from configparser import SafeConfigParser

from ccs import logger


class Config:

    CFG_FILE = 'ccs.ini'
    DEFAULT_CFG = {
        'lcd': {
            'device': '/dev/ttyAMA0',
            'width': 20,
            'height': 4,
        },
    }

    def init(self, settings_dir):
        """
        @brief      Initialize the config object. This is separate from the constructor so that
                    the object can be constructed without being initialized.

        @param      settings_dir  The directory to contain the config file
        """
        config_file = os.path.join(settings_dir, Config.CFG_FILE)
        self._config = SafeConfigParser()

        # Init default values
        for section, values in Config.DEFAULT_CFG.items():
            self._config[section] = values
        self._config.read(config_file)  # Read the file

        # Write back to the file
        with open(config_file, 'w') as f:
            self._config.write(f)

        logger.info(f"Loaded config with sections {self._config.sections()}")

    def __getitem__(self, item):
        return self._config[item]
