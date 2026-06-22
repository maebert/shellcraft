"""Each branch of BaseFactory.apply_effects (and prereq checks)."""

from shellcraft.events import Event


def test_apply_effects_enables_command(new_game):
    """Tutorial step 0 enables the `mine` and `reset` commands."""
    new_game.tutorial.apply_effects("0")
    assert "mine" in new_game.state.commands_enabled
    assert "reset" in new_game.state.commands_enabled


def test_apply_effects_enables_resource(new_game):
    new_game.tutorial.apply_effects("0")
    assert "clay" in new_game.state.resources_enabled


def test_apply_effects_enables_item(new_game):
    """Research 'small_cart' has effects.enable_items = 'small_cart'."""
    new_game.lab.apply_effects("small_cart")
    assert "small_cart" in new_game.state.tools_enabled


def test_apply_effects_is_idempotent(new_game):
    """Re-applying the same effect doesn't duplicate state or re-alert."""
    new_game.tutorial.apply_effects("0")
    new_game._messages.clear()
    new_game.tutorial.apply_effects("0")
    assert new_game.state.commands_enabled.count("mine") == 1
    assert new_game._messages == []


def test_apply_effects_modifies_mining_difficulty(new_game):
    """new_clay_deposit has effects.clay_mining_difficulty = 'random(.2, .5)';
    applying it should multiply current difficulty by (1 - change)."""
    new_game.mining_difficulty.clay = 1.0
    new_game.events.trigger("new_clay_deposit")
    # After random(.2, .5), difficulty is multiplied by (1 - 0.2..0.5) = 0.5..0.8
    assert 0.5 <= new_game.mining_difficulty.get("clay") <= 0.8


def test_events_trigger_alerts_description(new_game):
    new_game.events.trigger("new_clay_deposit")
    assert any("clay" in m for m in new_game._messages)


def test_prerequisite_items_block_availability(new_game):
    """A research project whose prereq lists a tool isn't available without that tool."""
    # automata research requires the 'nomenclator' trigger.
    assert new_game.lab.is_available("automata") is False
    new_game.state.triggers.append("nomenclator")
    assert new_game.lab.is_available("automata") is True


def test_prerequisite_research_blocks_tool_crafting(new_game):
    """small_cart tool requires research.small_cart."""
    new_game.state.tools_enabled = []
    new_game.resources.add("clay", 100)
    assert new_game.workshop.is_available("small_cart") is False
    new_game.state.research_completed.append("small_cart")
    assert new_game.workshop.is_available("small_cart") is True


def test_event_loaded_with_difficulty_modifier_string():
    """The string expression survives validation rather than being parsed early."""
    deposit = Event.get("new_clay_deposit")
    assert deposit.effects.clay_mining_difficulty == "random(.2, .5)"
    assert deposit.effects.ore_mining_difficulty is None
