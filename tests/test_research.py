"""Research workflow."""


def test_research_records_completion(new_game):
    new_game.state.resources_enabled.append("clay")
    new_game.resources.add("clay", 30)
    new_game.research("small_cart")
    assert "small_cart" in new_game.state.research_completed


def test_research_applies_enable_items_effect(new_game):
    """Researching small_cart unlocks the small_cart tool for crafting."""
    new_game.resources.add("clay", 30)
    new_game.research("small_cart")
    assert "small_cart" in new_game.state.tools_enabled


def test_research_unavailable_once_completed(new_game):
    new_game.resources.add("clay", 30)
    new_game.research("small_cart")
    assert new_game.lab.is_available("small_cart") is False


def test_research_not_available_when_prereq_unmet(new_game):
    """small_cart needs clay >= 20."""
    new_game.resources.add("clay", 5)
    assert new_game.lab.is_available("small_cart") is False


def test_research_available_when_prereq_met(new_game):
    new_game.resources.add("clay", 25)
    assert new_game.lab.is_available("small_cart") is True


def test_available_items_only_lists_eligible_research(new_game):
    new_game.resources.add("clay", 25)
    available = [p.name for p in new_game.lab.available_items]
    assert "small_cart" in available
    # dynamite needs ore >= 120 — not available.
    assert "dynamite" not in available
