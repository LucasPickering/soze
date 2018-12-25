import unittest

from soze_api import settings, util


class UtilTestCase(unittest.TestCase):
    def test_get_at_path(self):
        obj = {"led": {"color": 0x000000}, "lcd": {"color": 0xFF0000}}
        self.assertEqual(obj, util.get_at_path(obj, ""))

        # One level of nesting
        self.assertEqual(obj["lcd"], util.get_at_path(obj, "lcd"))

        # Nested value
        self.assertEqual(
            obj["lcd"]["color"], util.get_at_path(obj, "lcd:color")
        )

    def test_to_redis__full_obj(self):
        obj = settings.Settings.SETTINGS
        self.assertEqual(
            {
                "led:mode": obj["led"]["mode"],
                "led:static:color": obj["led"]["static"]["color"],
                "led:fade:colors": obj["led"]["fade"]["colors"],
                "led:fade:saved": obj["led"]["fade"]["saved"],
                "led:fade:fade_time": obj["led"]["fade"]["fade_time"],
                "lcd:mode": obj["lcd"]["mode"],
                "lcd:color": obj["lcd"]["color"],
                "lcd:link_to_led": obj["lcd"]["link_to_led"],
            },
            util.to_redis(obj, ""),
        )

    def test_to_redis__nested_obj(self):
        obj = settings.Settings.SETTINGS["lcd"]
        self.assertEqual(
            {
                "lcd:mode": obj["mode"],
                "lcd:color": obj["color"],
                "lcd:link_to_led": obj["link_to_led"],
            },
            util.to_redis(obj, "lcd"),
        )

    def test_to_redis__nested_value(self):
        val = settings.Settings.SETTINGS["lcd"]["mode"]
        self.assertEqual({"lcd:mode": val}, util.to_redis(val, "lcd:mode"))

    def test_from_redis__full_obj(self):
        obj = settings.Settings.SETTINGS

        # Full object
        self.assertEqual(
            obj,
            util.from_redis(
                {
                    "led:mode": obj["led"]["mode"],
                    "led:static:color": obj["led"]["static"]["color"],
                    "led:fade:colors": obj["led"]["fade"]["colors"],
                    "led:fade:saved": obj["led"]["fade"]["saved"],
                    "led:fade:fade_time": obj["led"]["fade"]["fade_time"],
                    "lcd:mode": obj["lcd"]["mode"],
                    "lcd:color": obj["lcd"]["color"],
                    "lcd:link_to_led": obj["lcd"]["link_to_led"],
                },
                "",
            ),
        )

    def test_from_redis__nested_obj(self):
        obj = settings.Settings.SETTINGS["lcd"]
        self.assertEqual(
            obj,
            util.from_redis(
                {
                    "lcd:mode": obj["mode"],
                    "lcd:color": obj["color"],
                    "lcd:link_to_led": obj["link_to_led"],
                },
                "lcd",
            ),
        )

    def test_from_redis__nested_val(self):
        val = settings.Settings.SETTINGS["lcd"]["mode"]
        self.assertEqual(val, util.from_redis({"lcd:mode": val}, "lcd:mode"))
