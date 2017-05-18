#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_shellcraft.

Tests for `shellcraft` module.
"""

from __future__ import unicode_literals

import pytest
from click.testing import CliRunner
from shellcraft.world import NPC


def test_npc_generation():
    """Test that we can generate random NPCs."""
    npc = NPC.generate()
    assert npc.name
    npc2 = NPC.generate()
    assert npc2.name != npc.name

