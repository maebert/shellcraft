#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_shellcraft.

Tests for `shellcraft` module.
"""

from __future__ import unicode_literals

from shellcraft.world import NPCFactory
from shellcraft.utils import format_name


def test_npc_generation():
    """Test that we can generate random NPCs."""
    npc = NPCFactory.make()
    assert format_name(npc)
    npc2 = NPCFactory.make()
    assert format_name(npc2) != format_name(npc)
