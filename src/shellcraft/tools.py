"""Tool catalog and factory."""

from typing import ClassVar, Dict

from pydantic import Field

from shellcraft.core import BaseFactory, BaseItem


class Tool(BaseItem):
    """A craftable tool. Definition data; runtime instances live in game_state."""

    type: str = "tool"
    durability: float = -1
    mining_bonus: Dict[str, float] = Field(default_factory=dict)
    event_bonus: Dict[str, float] = Field(default_factory=dict)
    crafting_bonus: Dict[str, float] = Field(default_factory=dict)
    research_bonus: float = 0

    FIXTURES: ClassVar[str] = "tools.toml"

    def describe_wear(self, condition: float) -> str:
        """Return a human description of a given tool's condition."""
        if self.durability == -1 or self.durability == condition:
            return f"${self.name}$"
        wear = condition / self.durability
        descriptions = {
            1: "new",
            0.9: "slightly used",
            0.8: "used",
            0.6: "worn",
            0.3: "damaged",
            0.15: "about to break",
        }
        for thresh, des in sorted(descriptions.items()):
            if wear < thresh:
                return f"${self.name}$ ({des})"
        return f"${self.name}$"


class ToolFactory(BaseFactory):
    ITEM_CLASS = Tool

    def is_available(self, item_name):
        item = self.get(item_name)
        if item.name in self.game.state.tools_enabled:
            return True
        return super().is_available(item)


# Populate the catalog at import time.
Tool._load_catalog()
