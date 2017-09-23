import unittest

from ccs.lcd.helper import diff_text


class HelperTestCase(unittest.TestCase):

    def test_diff_text_one_line(self):
        d = diff_text(['abc'], ['abc'])
        self.assertEqual({}, d)

        d = diff_text(['abc'], ['1bc'])
        self.assertEqual({(0, 0): '1'}, d)

        d = diff_text(['abc'], ['12c'])
        self.assertEqual({(0, 0): '12'}, d)

        d = diff_text(['abc'], ['a12'])
        self.assertEqual({(1, 0): '12'}, d)

        d = diff_text(['abcde'], ['1bc'])
        self.assertEqual({(0, 0): '1', (3, 0): '  '}, d)

    def test_diff_text_multiline(self):
        d = diff_text(['abc', 'def'], ['abc', 'def'])
        self.assertEqual({}, d)

        d = diff_text(['abc', 'def'], ['abc', 'fed'])
        self.assertEqual({(0, 1): 'f', (2, 1): 'd'}, d)

        d = diff_text(['abc', 'def'], ['abc'])
        self.assertEqual({(0, 1): '   '}, d)

        d = diff_text(['   abc', 'def'], ['abc', 'fed   '])
        self.assertEqual({(0, 0): 'abc   ', (0, 1): 'f', (2, 1): 'd'}, d)

        d = diff_text(['', '', ''], ['abcdefgh', '123456', '   wxyz'])
        self.assertEqual({(0, 0): 'abcdefgh', (0, 1): '123456', (3, 2): 'wxyz'}, d)
