"""Protect the real contribution data while changing its presentation."""
import importlib.util
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('snake', ROOT/'scripts/prepare_snake.py')
snake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snake)


class SnakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = (ROOT/'assets/source/contribution-snake.svg').read_text()
        cls.animated, cls.static = snake.enhance(cls.original)

    def test_every_contribution_cell_and_its_activity_keyframes_are_preserved(self):
        def cells(source):
            return [dict(el.attrib) for el in ET.fromstring(source).iter()
                    if 'c' in el.get('class', '').split()]
        self.assertGreater(len(cells(self.original)), 300)
        self.assertEqual(cells(self.original), cells(self.animated))
        self.assertEqual(cells(self.original), cells(self.static))
        def keyframes(source):
            return re.findall(r'@keyframes\s+[^{}]+\{(?:[^{}]*\{[^{}]*\})+\}', source)
        original=keyframes(self.original)
        self.assertEqual(original, keyframes(self.animated)[:len(original)])

    def test_skin_uses_the_real_head_route_and_reduced_motion_is_explicit(self):
        self.assertRegex(self.animated, r'\.trail\{[^}]+animation:skin-motion [\d.]+s linear infinite')
        self.assertIn('*{animation:none!important}', self.static)
        self.assertIn('.trail,.s,.u{display:none}', self.static)
        self.assertIn('id="reduced-motion"', self.animated)
        self.assertIn('svg:target *{animation:none!important}', self.animated)

    def test_smoothed_skin_stays_within_four_pixels_of_real_calendar_route(self):
        route=snake.head_route(self.original)
        frames=re.findall(r'([\d.]+)%\{transform:translate\((-?[\d.]+)px,(-?[\d.]+)px\) rotate\((-?[\d.]+)deg\)\}',self.animated)
        self.assertGreater(len(frames),600)
        for percent,x,y,angle in frames:
            real=route(float(percent)/100)
            self.assertLessEqual(((float(x)-8-real[0])**2+(float(y)-8-real[1])**2)**.5,4)

    def test_reprocessing_or_unknown_geometry_fails_before_publication(self):
        with self.assertRaises(ValueError):
            snake.enhance(self.animated)
        with self.assertRaises(ValueError):
            snake.enhance(self.original.replace('880 192', '900 192'))


if __name__ == '__main__':
    unittest.main()
