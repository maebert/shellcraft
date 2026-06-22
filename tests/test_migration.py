"""Characterization tests for the protobuf-shim → pure-Pydantic migration.

These exercise behavior that must survive the refactor: save/load round-trips,
tool wear, catalog joins, resource arithmetic, fraction seeding, and
backward compat with the existing save1.json fixture.

Tests are written against stable surface APIs (Game.mine/craft, game.resources.get,
workshop.get) rather than internal proxy types, so they pin behavior on both
sides of the migration without modification.
"""

import os

import pytest

from shellcraft.shellcraft import Game


@pytest.fixture
def fresh_game(tmp_path):
    """A new game in debug mode with clay mining and shovel crafting unlocked."""
    save_path = tmp_path / "save.json"
    game = Game.create(str(save_path))
    game.state.debug = True
    game.state.resources_enabled.append("clay")
    game.state.tools_enabled.append("shovel")
    game.state.action = None
    return game


def _settle(game):
    """Clear the in-progress action so the next call isn't BusyException-blocked."""
    game.state.action = None


def test_save_load_roundtrip_preserves_tool_condition(fresh_game):
    """A crafted tool survives save/load with its persisted condition intact."""
    game = fresh_game
    game.resources.add("clay", 10)
    _settle(game)
    game.craft("shovel")
    game.save()

    reloaded = Game.load(game.save_file)
    tools = list(reloaded.tools)
    assert len(tools) == 1
    assert tools[0].name == "shovel"
    # Fresh craft → full durability of 16 (per tools.toml).
    assert tools[0].condition == 16


def test_loaded_tool_can_be_used_for_mining(fresh_game):
    """The bug from the original report: a re-loaded tool degrades without crashing."""
    game = fresh_game
    game.resources.add("clay", 10)
    _settle(game)
    game.craft("shovel")
    game.save()

    reloaded = Game.load(game.save_file)
    _settle(reloaded)
    reloaded.mine("clay")
    [tool] = list(reloaded.tools)
    assert tool.condition < 16  # wore down


def test_tool_wears_then_destroys_without_error(fresh_game):
    """Mining repeatedly drives condition to 0; destruction must not crash."""
    game = fresh_game
    game.resources.add("clay", 4)
    _settle(game)
    game.craft("shovel")

    conditions = []
    destroyed = False
    for _ in range(20):
        _settle(game)
        game.mine("clay")
        tools = list(game.tools)
        if not tools:
            destroyed = True
            break
        conditions.append(tools[0].condition)

    assert conditions[0] < 16  # first mine wore it
    assert conditions == sorted(conditions, reverse=True)  # monotonically degrading
    assert destroyed  # eventually removed from the list


def test_catalog_lookup_for_saved_tool(fresh_game):
    """A name-only saved tool can still resolve its static catalog data."""
    game = fresh_game
    game.resources.add("clay", 10)
    _settle(game)
    game.craft("shovel")
    game.save()

    reloaded = Game.load(game.save_file)
    [tool] = list(reloaded.tools)
    catalog = reloaded.workshop.get(tool.name)
    assert catalog.durability == 16
    assert catalog.mining_bonus["clay"] == 2


def test_resources_arithmetic_get_add(fresh_game):
    """Resource accessors: get returns 0 by default, add accumulates."""
    game = fresh_game
    assert game.resources.get("clay") == 0
    game.resources.add("clay", 5)
    game.resources.add("clay", 3)
    assert game.resources.get("clay") == 8
    game.resources.add("clay", -2)
    assert game.resources.get("clay") == 6


def test_mining_difficulty_multiply(fresh_game):
    """multiply scales the current value and is observable via get."""
    game = fresh_game
    starting = game.mining_difficulty.get("clay")
    game.mining_difficulty.multiply("clay", 0.5)
    assert game.mining_difficulty.get("clay") == pytest.approx(starting * 0.5)


def test_legacy_fixture_loads(tmp_path):
    """tests/fixtures/save1.json (the historical save format) loads cleanly."""
    fixture = os.path.join(os.path.dirname(__file__), "fixtures", "save1.json")
    game = Game.load(fixture)

    assert game.resources.get("clay") == 30
    assert game.resources.get("ore") == 120

    tools_by_name = {t.name: t.condition for t in game.tools}
    assert tools_by_name["sturdy_shovel"] == 42.5
    assert tools_by_name["axe"] == 457.5

    assert game.workshop.get("sturdy_shovel").durability == 96
    assert game.workshop.get("axe").mining_bonus["ore"] == 8


def test_save_load_roundtrip_via_json(fresh_game):
    """Saving then re-loading produces an equivalent state."""
    import json

    game = fresh_game
    game.resources.add("clay", 4)
    game.resources.add("ore", 2)
    _settle(game)
    game.craft("shovel")
    game.save()

    with open(game.save_file) as f:
        payload = json.load(f)

    # Save format contract: tools serialize as {name, condition} only.
    assert payload["tools"] == [{"name": "shovel", "condition": 16.0}]
    assert payload["resources"]["clay"] == 0  # spent on the craft
    assert payload["resources"]["ore"] == 2

    reloaded = Game.load(game.save_file)
    assert reloaded.resources.get("ore") == 2
    [tool] = list(reloaded.tools)
    assert tool.name == "shovel" and tool.condition == 16
