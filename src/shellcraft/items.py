# -*- coding: utf-8 -*-
"""Item Classes."""
from __future__ import absolute_import

from shellcraft.core import Item


class ClayShovel(Item):
    """Basic clay mining item."""

    durability = 5
    mining_bonus = {'clay': 1.1}
    cost = {'clay': 6}


class SturdyClayShovel(ClayShovel):
    """Better clay mining item."""

    durability = 10
    cost = {'clay': 10}
