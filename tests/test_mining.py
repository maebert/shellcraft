"""Mining mechanics in depth."""

import pytest

from shellcraft.exceptions import BusyException


def _settle(game):
    game.state.action = None


def test_hand_mining_yields_clay(new_game):
    """No tools, no mining bonus — base efficiency 1."""
    new_game.state.resources_enabled.append("clay")
    new_game.mine("clay")
    assert new_game.resources.get("clay") == 1


def test_mining_with_shovel_doubles_yield(shovel_game):
    """Shovel grants 2x mining_bonus.clay; first mine yields 2."""
    shovel_game.craft("shovel")
    _settle(shovel_game)
    starting = shovel_game.resources.get("clay")
    shovel_game.mine("clay")
    assert shovel_game.resources.get("clay") == starting + 2


def test_mining_difficulty_increments_after_each_mine(shovel_game):
    starting = shovel_game.mining_difficulty.get("clay")
    increment = shovel_game.mining_difficulty_increment.get("clay")
    shovel_game.mine("clay")
    assert shovel_game.mining_difficulty.get("clay") == pytest.approx(
        starting + increment
    )


def test_mining_busy_state_raises(shovel_game):
    """When debug mode is off, the in-progress action blocks the next call."""
    shovel_game.state.debug = False
    shovel_game.mine("clay")
    with pytest.raises(BusyException):
        shovel_game.mine("clay")


def test_total_mined_accumulates(shovel_game):
    """The lifetime stat tracks every successful mine."""
    for _ in range(3):
        _settle(shovel_game)
        shovel_game.mine("clay")
    assert shovel_game.total_mined.get("clay") >= 3


def test_best_tool_picked_when_multiple_present(shovel_game):
    """With shovel + sturdy_shovel both available, sturdy_shovel has higher
    nominal durability but the same mining_bonus.clay=2; both contribute, but
    the shovel (best by mining_bonus tie → max returns first matching) handles
    the work. This test mainly confirms the selector finds *something* sensible."""
    shovel_game.state.tools_enabled.append("sturdy_shovel")
    shovel_game.resources.add("clay", 10)
    shovel_game.craft("shovel")
    _settle(shovel_game)
    shovel_game.craft("sturdy_shovel")
    _settle(shovel_game)
    starting = shovel_game.resources.get("clay")
    shovel_game.mine("clay")
    # Some clay was mined.
    assert shovel_game.resources.get("clay") > starting


def test_tool_destroyed_during_mine_emits_alert(shovel_game):
    """When a tool's condition runs out mid-mine, it's removed and alerted."""
    shovel_game.craft("shovel")
    _settle(shovel_game)
    # Drive difficulty past the shovel's durability quickly.
    shovel_game.mining_difficulty.add("clay", 30)
    shovel_game.mine("clay")
    assert len(shovel_game.tools) == 0
    assert any("Destroyed" in m for m in shovel_game._messages)
