"""Tests for the catalog registry: lookup, parsing, scalar→list coercion."""

import pytest

from shellcraft.core import Effects, Prerequisites
from shellcraft.events import Event
from shellcraft.research import ResearchProject
from shellcraft.tools import Tool
from shellcraft.tutorial import Step


def test_tool_catalog_has_known_entries():
    """The TOML catalog populates at import time."""
    tools = Tool.all()
    assert "shovel" in tools
    assert "sturdy_shovel" in tools
    assert "small_cart" in tools


def test_tool_lookup_returns_catalog_entry():
    shovel = Tool.get("shovel")
    assert shovel.name == "shovel"
    assert shovel.durability == 16
    assert shovel.mining_bonus == {"clay": 2}
    assert shovel.cost.clay == 4


def test_tool_lookup_unknown_raises():
    with pytest.raises(ValueError, match="Tool 'no_such_tool' not found"):
        Tool.get("no_such_tool")


def test_research_catalog_loaded():
    project = ResearchProject.get("small_cart")
    assert project.difficulty == 120
    assert project.prerequisites.clay == 20
    # Scalar TOML value coerced to list.
    assert project.effects.enable_items == ["small_cart"]


def test_event_catalog_loaded():
    deposit = Event.get("new_clay_deposit")
    assert "clay" in deposit.description
    # Effects on events: mining-difficulty modifier as a string expression.
    assert deposit.effects.clay_mining_difficulty == "random(.2, .5)"


def test_tutorial_step_loaded():
    step = Step.get("0")
    assert "ShellCraft" in step.description
    assert step.effects.enable_resources == ["clay"]
    # List-valued field stays a list.
    assert step.effects.enable_commands == ["mine", "reset"]


def test_prerequisites_scalar_string_coerced_to_list():
    p = Prerequisites.model_validate({"research": "small_cart"})
    assert p.research == ["small_cart"]


def test_prerequisites_list_stays_list():
    p = Prerequisites.model_validate({"items": ["shovel", "axe"]})
    assert p.items == ["shovel", "axe"]


def test_effects_scalar_coercion_across_fields():
    e = Effects.model_validate(
        {
            "enable_commands": "mine",
            "enable_items": "shovel",
            "enable_resources": "ore",
            "events": "new_clay_deposit",
            "triggers": "nomenclator",
        }
    )
    assert e.enable_commands == ["mine"]
    assert e.enable_items == ["shovel"]
    assert e.enable_resources == ["ore"]
    assert e.events == ["new_clay_deposit"]
    assert e.triggers == ["nomenclator"]


def test_effects_none_becomes_empty_list():
    e = Effects.model_validate({"enable_commands": None})
    assert e.enable_commands == []


def test_get_by_existing_instance_returns_same():
    """Passing a catalog instance back through get() is a no-op."""
    shovel = Tool.get("shovel")
    assert Tool.get(shovel) is shovel
