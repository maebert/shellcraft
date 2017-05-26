# coding=utf-8

"""World generation tools."""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import random

from shellcraft.grammar import Grammar


class NPC(object):
    """A character in the game that may have a political affiliation, job, and attitude to the player."""

    namer = Grammar.grammars['names']

    def __init__(self, first, middle, last, title=None, nickname=None, display=None):
        """Create the character from scratch."""
        self.first = first
        self.middle = middle
        self.last = last
        self.title = title
        self.nickname = nickname
        self._display = display
        self.fraction = None

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
        last = cls.namer.generate("@family")
        nobility = int((random.random() ** nobility_factor) * 4)
        nickname = cls.namer.generate("@nickname") if not nobility and random.random() < .1 else ""
        if gender:
            first = cls.namer.generate("@female")
            middle = cls.namer.generate("@female")
            title = ['', 'Lady', 'Baroness', 'Countess'][nobility]
        else:
            first = cls.namer.generate("@male")
            middle = cls.namer.generate("@male")
            title = ['', 'Lord', 'Baron', 'Earl'][nobility]
        display = cls.namer.generate("@display_nickname") if nickname else cls.namer.generate("@display")
        return cls(first, middle, last, title, nickname, display)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{}>".format(self.name)
