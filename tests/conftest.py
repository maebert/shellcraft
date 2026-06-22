"""Shared test fixtures."""

import pytest

from shellcraft.shellcraft import Game


@pytest.fixture
def new_game(tmp_path):
    """A debug-mode game with no progress.

    No commands enabled, no resources unlocked — set what you need per test.
    Debug mode means actions complete instantly.
    """
    game = Game.create(str(tmp_path / "save.json"))
    game.state.debug = True
    game.state.action = None
    return game


@pytest.fixture
def shovel_game(new_game):
    """Game with clay unlocked, shovel craftable, and 10 clay in hand."""
    new_game.state.resources_enabled.append("clay")
    new_game.state.tools_enabled.append("shovel")
    new_game.resources.add("clay", 10)
    return new_game
