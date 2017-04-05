# -*- coding: utf-8 -*-
"""Item Classes."""
from __future__ import absolute_import

from shellcraft.core import Item


class ClayShovel(Item):
    """Basic clay mining item."""

    durability = 30
    mining_bonus = {'clay': 2}
    cost = {'clay': 4}
    prerequisites = {'resources_required': {'clay': 4}}


class SturdyClayShovel(ClayShovel):
    """Better clay mining item."""

    durability = 120
    cost = {'clay': 10}
    prerequisites = {'resources_required': {'clay': 10}}
