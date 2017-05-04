# coding=utf-8

"""World generation tools."""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import random

from shellcraft.grammar import GUILDS, NAMES


class Fraction(object):
    """Each fraction battles for influence."""

    def __init__(self, name):
        """Create a new fraction from scratch."""
        self.name = name

    @classmethod
    def generate(cls):
        """Generate a random fraction."""
        fraction = cls(GUILDS.generate())
        fraction.power = random.random()
        fraction.leader = NPC.generate(nobility_factor=2)
        fraction.leader_title = GUILDS.generate("leader_role")

        fraction.aristocracy = (2 * random.random() - 1) ** 3
        fraction.theocracy = (2 * random.random() - 1) ** 3
        fraction.mercantilism = (2 * random.random() - 1) ** 3
        fraction.industrialism = (2 * random.random() - 1) ** 3

        return fraction


class NPC(object):
    """A character in the game that may have a political affiliation, job, and attitude to the player."""

    def __init__(self, first, middle, last, title=None, nickname=None, display=None):
        """Create the character from scratch."""
        self.first = first
        self.middle = middle
        self.last = last
        self.title = title
        self.nickname = nickname
        self._display = display

    @property
    def name(self):
        """Generate the display name of the person."""
        return self._display.format(
            first=self.first,
            middle=self.middle,
            last=self.last,
            title=self.title,
            nickname=self.nickname,
            first_initial=self.first[0] + ".",
            middle_initial=self.middle[0] + "."
        ).strip()

    @classmethod
    def generate(cls, nobility_factor=8):
        """Generate a random NPC."""
        gender = random.randint(0, 1)
        last = NAMES.generate("family")
        nobility = int((random.random() ** nobility_factor) * 4)
        nickname = NAMES.generate("nickname") if not nobility and random.random() < .1 else ""
        if gender:
            first = NAMES.generate("female")
            middle = NAMES.generate("female")
            title = ['', 'Lady', 'Baroness', 'Countess'][nobility]
        else:
            first = NAMES.generate("male")
            middle = NAMES.generate("female")
            title = ['', 'Lord', 'Baron', 'Earl'][nobility]
        display = NAMES.generate("display_nickname") if nickname else NAMES.generate("display")
        return cls(first, middle, last, title, nickname, display)
