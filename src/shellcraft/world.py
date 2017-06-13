# coding=utf-8

"""World generation tools."""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import random

from shellcraft.grammar import Grammar
from shellcraft.game_state_pb2 import NPC as NPCPB


class NPCFactory(object):
    """A character in the game that may have a political affiliation, job, and attitude to the player."""

    namer = Grammar.grammars['names']

    @classmethod
    def make(cls, nobility_factor=8, fraction=None):
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

        return NPCPB(
            first=first,
            middle=middle,
            last=last,
            title=title,
            nickname=nickname,
            display=display
        )
