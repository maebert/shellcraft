# -*- coding: utf-8 -*-
"""Item Classes."""
from shellcraft.core import BaseItem, BaseFactory
from shellcraft.game_state_pb2 import Tool as ToolPB


class Tool(BaseItem):
    """Concept denoting any tool that the player can produce."""

    @classmethod
    def from_dict(cls, name, data):
        tool = super(Tool, cls).from_dict(name, data)
        tool.type = data.get("type", "tool")
        tool.durability = data.get("durability", -1)
        tool.mining_bonus = data.get("mining_bonus", {})
        tool.event_bonus = data.get("event_bonus", {})
        tool.crafting_bonus = data.get("crafting_bonus", {})
        tool.research_bonus = data.get("research_bonus", 0)
        return tool

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
