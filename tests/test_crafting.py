"""Crafting workflow and error paths."""

import pytest

from shellcraft.exceptions import BusyException


def test_craft_deducts_resource_cost(shovel_game):
    """Cost is removed from the player's resources on craft."""
    starting = shovel_game.resources.get("clay")
    shovel_game.craft("shovel")
    assert shovel_game.resources.get("clay") == starting - 4


def test_craft_adds_tool_with_full_durability(shovel_game):
    shovel_game.craft("shovel")
    [tool] = list(shovel_game.tools)
    assert tool.name == "shovel"
    assert tool.condition == 16  # full durability from tools.toml


def test_can_afford_true_when_resources_sufficient(shovel_game):
    assert shovel_game.workshop.can_afford("shovel") is True


def test_can_afford_false_when_resources_lacking(new_game):
    """With no clay, the shovel is not affordable."""
    assert new_game.workshop.can_afford("shovel") is False


def test_resources_missing_to_craft(new_game):
    missing = new_game.workshop._resources_missing_to_craft("shovel")
    assert missing == {"clay": 4}


def test_busy_blocks_a_second_craft(shovel_game):
    """Toggle off debug mode so the action lingers; second craft must raise."""
    shovel_game.state.debug = False
    shovel_game.resources.add("clay", 4)  # enough for two shovels
    shovel_game.craft("shovel")
    with pytest.raises(BusyException) as exc_info:
        shovel_game.craft("shovel")
    message = str(exc_info.value)
    # Message includes the verb, the target, and a duration.
    assert "crafting shovel" in message
    assert "for another" in message
    assert message.endswith(".")


def test_crafting_an_automaton_lands_in_automata_not_tools(new_game):
    """small_cart has no `type` field → defaults to 'tool'; crawler is an automaton."""
    new_game.state.resources_enabled.append("clay")
    new_game.state.resources_enabled.append("ore")
    new_game.state.tools_enabled.append("crawler")
    new_game.resources.add("clay", 40)
    new_game.resources.add("ore", 40)
    new_game.state.research_completed.append("automata")

    new_game.craft("crawler")
    assert len(new_game.tools) == 0
    assert len(new_game.automata) == 1
    assert new_game.automata[0].name == "crawler"


def test_has_item_returns_true_after_craft(shovel_game):
    shovel_game.craft("shovel")
    assert shovel_game.has_item("shovel") is True
    assert shovel_game.has_item("axe") is False
