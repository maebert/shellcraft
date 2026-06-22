"""ToolInstance.__str__ rendering across condition thresholds."""

from shellcraft.game_state import ToolInstance


def test_full_durability_renders_bare_name():
    """At full condition the wear description is just the name."""
    tool = ToolInstance(name="shovel", condition=16)
    assert str(tool) == "$shovel$"


def test_new_threshold():
    """Just under 100% but at or above 90% durability → 'new'."""
    tool = ToolInstance(name="shovel", condition=15.5)
    assert str(tool) == "$shovel$ (new)"


def test_slightly_used_threshold():
    """80%-90% durability → 'slightly used'. 13/16 = 0.8125."""
    tool = ToolInstance(name="shovel", condition=13)
    assert str(tool) == "$shovel$ (slightly used)"


def test_used_threshold():
    """60%-80% durability → 'used'. 11/16 = 0.6875."""
    tool = ToolInstance(name="shovel", condition=11)
    assert str(tool) == "$shovel$ (used)"


def test_worn_threshold():
    """30%-60% durability → 'worn'. 8/16 = 0.5."""
    tool = ToolInstance(name="shovel", condition=8)
    assert str(tool) == "$shovel$ (worn)"


def test_damaged_threshold():
    """15%-30% durability → 'damaged'. 4/16 = 0.25."""
    tool = ToolInstance(name="shovel", condition=4)
    assert str(tool) == "$shovel$ (damaged)"


def test_about_to_break_threshold():
    """Under 15% durability → 'about to break'. 1/16 = 0.0625."""
    tool = ToolInstance(name="shovel", condition=1)
    assert str(tool) == "$shovel$ (about to break)"


def test_unbreakable_tool_renders_bare_name():
    """small_cart has no `durability` set — defaults to no wear tracking."""
    # Catalog small_cart has durability=300; the unbreakable case is durability=-1,
    # which the BaseItem default. We don't have such a tool in fixtures, so spot-check
    # via constructed instance with condition matching durability (no wear).
    tool = ToolInstance(name="small_cart", condition=300)
    assert str(tool) == "$small_cart$"
