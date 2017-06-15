#!/usr/bin/env python
# encoding: utf-8

"""Module documentation."""

from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import str

__author__ = 'Manuel Ebert'
__email__ = 'manuel@1450.me'


class Color(object):
    """Truecolor."""

    def __init__(self, r=None, g=None, b=None):
        """Initialise the color.

        Examples:
            >>> Color('F6BA4C')
            >>> Color(264, 186, 76)
        """
        if isinstance(r, str):
            self.rgb = int(r[:2], 16), int(r[2:4], 16), int(r[4:], 16)
        elif r and g and b:
            self.rgb = int(r), int(g), int(b)

    @property
    def ansi(self):
        """Generate ANSI escape sequence for color."""
        return "\x1b[38;2;{};{};{}m".format(*self.rgb)

    @property
    def clear(self):
        """Generate ANSI escape sequence for unsetting color."""
        return "\x1b[0m"

    def __call__(self, text):
        """Format a text with the given color."""
        return self.ansi + text + self.clear

    def mix(self, other, ratio):
        """Return an RGB blend between this and another color.

        Args:
            other (color)
            ratio (float): Ratio between 0 (100% this) and 1 (100% other)
        """
        ratio = min(1, max(ratio, 0))
        return Color(*[
            (1 - ratio) * s + ratio * o for s, o in zip(self.rgb, other.rgb)
        ])


class Gradient(object):
    """Represents a gradient for colours."""

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def _generate(self, ratio=.5):
        """Generate a color given a value.

        Args:
            pos (float): Value in [0, 1]
        """
        return self.start.mix(self.end, ratio)

    def __call__(self, text, ratio=.5):
        """Format a text with the given color."""
        mix = self._generate(ratio)
        return mix.ansi + text + mix.clear

Color.yellow = Color('F5C065')
Color.green = Color('58BD86')
Color.blue = Color('798BDF')
Color.purple = Color('AB81B8')
Color.red = Color('E8685D')
Color.pink = Color('F25C80')
Color.grey = Color('91B1C1')
Color.dark = Color('2B333F')
Color.white = Color('ffffff')

Gradient.yellow = Gradient(Color.dark, Color.yellow)
Gradient.green = Gradient(Color.dark, Color.green)
Gradient.dark = Gradient(Color.dark, Color('3D495A'))
