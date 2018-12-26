import unittest

from soze_api import setting


class ModeSettingTestCase(unittest.TestCase):
    def setUp(self):
        self.setting = setting.ModeSetting(["off", "on"], "off")

    def test_to_redis(self):
        self.assertEqual("off", self.setting.to_redis("off"))

        self.assertRaises(ValueError, lambda: self.setting.to_redis("fake"))
        self.assertRaises(ValueError, lambda: self.setting.to_redis(True))

    def test_from_redis(self):
        self.assertEqual("off", self.setting.from_redis(None))
        self.assertEqual("off", self.setting.from_redis(b"off"))


class ColorSettingTestCase(unittest.TestCase):
    def setUp(self):
        self.setting = setting.ColorSetting()

    def test_to_redis(self):
        self.assertEqual(0x000000, self.setting.to_redis(0x000000))

        self.assertRaises(ValueError, lambda: self.setting.to_redis(-1))
        self.assertRaises(ValueError, lambda: self.setting.to_redis(0x1000000))
        self.assertRaises(ValueError, lambda: self.setting.to_redis(True))

    def test_from_redis(self):
        self.assertEqual(0x000000, self.setting.from_redis(None))
        self.assertEqual(0x0000FF, self.setting.from_redis(b"255"))


class BoolSettingTestCase(unittest.TestCase):
    def setUp(self):
        self.setting = setting.BoolSetting()

    def test_to_redis(self):
        self.assertEqual("False", self.setting.to_redis(False))
        self.assertEqual("True", self.setting.to_redis(True))

        self.assertRaises(ValueError, lambda: self.setting.to_redis("True"))

    def test_from_redis(self):
        self.assertEqual(False, self.setting.from_redis(None))

        self.assertEqual(False, self.setting.from_redis(b"false"))
        self.assertEqual(False, self.setting.from_redis(b"False"))

        self.assertEqual(True, self.setting.from_redis(b"true"))
        self.assertEqual(True, self.setting.from_redis(b"True"))


class FloatSettingTestCase(unittest.TestCase):
    def setUp(self):
        self.setting = setting.FloatSetting(5.0, 1.0, 10.0)

    def test_to_redis(self):
        self.assertEqual(5.0, self.setting.to_redis(5.0))
        self.assertEqual(5.0, self.setting.to_redis(5))

        self.assertRaises(ValueError, lambda: self.setting.to_redis(0.9))
        self.assertRaises(ValueError, lambda: self.setting.to_redis(10.1))
        self.assertRaises(ValueError, lambda: self.setting.to_redis(True))

    def test_from_redis(self):
        self.assertEqual(5.0, self.setting.from_redis(None))
        self.assertEqual(1.0, self.setting.from_redis(b"1.0"))


class ListSettingTestCase(unittest.TestCase):
    def setUp(self):
        self.setting = setting.ListSetting(setting.BoolSetting())

    def test_to_redis(self):
        self.assertEqual("[false]", self.setting.to_redis([False]))

        self.assertRaises(ValueError, lambda: self.setting.to_redis(["True"]))
        self.assertRaises(ValueError, lambda: self.setting.to_redis(True))

    def test_from_redis(self):
        self.assertEqual([], self.setting.from_redis(None))
        self.assertEqual([False], self.setting.from_redis(b"[false]"))


class DictSettingTestCase(unittest.TestCase):
    def setUp(self):
        self.setting = setting.DictSetting(setting.BoolSetting())

    def test_to_redis(self):
        self.assertEqual('{"k": false}', self.setting.to_redis({"k": False}))

        self.assertRaises(
            ValueError, lambda: self.setting.to_redis({"k": "False"})
        )
        self.assertRaises(ValueError, lambda: self.setting.to_redis(True))

    def test_from_redis(self):
        self.assertEqual({}, self.setting.from_redis(None))
        self.assertEqual({"k": False}, self.setting.from_redis(b'{"k": false}'))
