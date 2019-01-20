import pickle
import unittest

from soze_api.resource import Settings
from soze_api.setting import (
    ColorSetting,
    DictSetting,
    EnumSetting,
    FloatSetting,
    ListSetting,
)


class SettingsTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(
            {
                "enum": EnumSetting(["off", "on"], "off"),
                "dict": DictSetting(FloatSetting(0.0)),
                "nested": {"list": ListSetting(FloatSetting(0.0))},
            }
        )

        self.led_settings = Settings(
            {
                "mode": EnumSetting(["off", "static", "fade"], "off"),
                "static": {"color": ColorSetting()},
                "fade": {
                    "colors": ListSetting(ColorSetting()),
                    "saved": DictSetting(ListSetting(ColorSetting())),
                    "fade_time": FloatSetting(5.0, 1.0, 30.0),
                },
            }
        )

    def test_merge(self):
        self.assertEqual(
            {"enum": "on"}, self.settings.merge({"enum": "off"}, {"enum": "on"})
        )

        # Test that Dict and List settings don't get merged
        self.assertEqual(
            {"dict": {"k2": 2.0}, "nested": {"list": [2.0]}},
            self.settings.merge(
                {"dict": {"k1": 1.0}, "nested": {"list": [1.0]}},
                {"dict": {"k2": 2.0}, "nested": {"list": [2.0]}},
            ),
        )

        self.assertEqual(
            {"nested": {"list": [1.0]}},
            self.settings.merge({"nested": {"list": [1.0]}}, {}),
        )

        self.assertEqual(
            {"enum": "off", "nested": {"list": [2.0]}},
            self.settings.merge(
                {"enum": "off", "nested": {"list": [1.0]}},
                {"nested": {"list": [2.0]}},
            ),
        )

    def test_from_redis(self):
        self.assertEqual(
            {"enum": "off", "dict": {}, "nested": {"list": []}},
            self.settings.from_redis({}),
        )

        self.assertEqual(
            {"enum": "on", "dict": {"k1": 1.0}, "nested": {"list": [1.0]}},
            self.settings.from_redis(
                {
                    "enum": b"on",
                    "dict": pickle.dumps({"k1": 1.0}),
                    "nested": {"list": pickle.dumps([1.0])},
                }
            ),
        )

    def test_to_redis(self):
        self.assertEqual({}, self.settings.to_redis({}))

        self.assertEqual(
            {"enum": b"on", "nested": {"list": pickle.dumps([1.0])}},
            self.settings.to_redis({"enum": "on", "nested": {"list": [1.0]}}),
        )
