# -*- coding: utf-8 -*-
"""Item Classes."""
from typing import Dict
from pydantic import Field
from shellcraft.core import BaseItem, BaseFactory
from shellcraft.game_state import Tool as ToolPB


class Tool(BaseItem):
    """Concept denoting any tool that the player can produce."""

    type: str = "tool"
    durability: float = -1
    mining_bonus: Dict[str, float] = Field(default_factory=dict)
    event_bonus: Dict[str, float] = Field(default_factory=dict)
    crafting_bonus: Dict[str, float] = Field(default_factory=dict)
    research_bonus: float = 0

    # Tool condition (runtime only, not in template)
    condition: float = Field(default=0, exclude=True)

    @classmethod
    def from_dict(cls, name, data):
        # Process base item data first
        tool = super(Tool, cls).from_dict(name, data)

        # Update with tool-specific data
        tool_data = {
            'type': data.get("type", "tool"),
            'durability': data.get("durability", -1),
            'mining_bonus': data.get("mining_bonus", {}),
            'event_bonus': data.get("event_bonus", {}),
            'crafting_bonus': data.get("crafting_bonus", {}),
            'research_bonus': data.get("research_bonus", 0),
        }

        # Create new Tool instance with all data
        return cls(
            name=tool.name,
            description=tool.description,
            difficulty=tool.difficulty,
            prerequisites=tool.prerequisites,
            cost=tool.cost,
            effects=tool.effects,
            strings=tool.strings,
            **tool_data
        )

    def __repr__(self):
        """Representation, e.g. 'clay_shovel (worn)'."""
        if (
            not hasattr(self, "condition")
            or self.durability == -1
            or self.durability == self.condition
        ):
            return f"${self.name}$"

        wear = 1.0 * self.condition / self.durability
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


class ToolFactory(BaseFactory):
    FIXTURES = "tools.toml"
    ITEM_CLASS = Tool
    PB_CLASS = ToolPB

    def make(self, source):
        tool = super(ToolFactory, self).make(source)
        if not hasattr(tool, "condition"):
            tool.condition = tool.durability
        return tool

    def is_available(self, item_name):
        item = self.get(item_name)
        return item.name in self.game.state.tools_enabled or super(
            ToolFactory, self
        ).is_available(item)
