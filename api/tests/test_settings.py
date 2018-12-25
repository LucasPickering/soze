import unittest

from soze_api import settings


class SettingsTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = settings.Settings("redis://localhost:6379/0")
