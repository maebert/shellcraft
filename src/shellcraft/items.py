# -*- coding: utf-8 -*-
"""Item Classes."""
from __future__ import absolute_import

from shellcraft.core import AbstractItem, AbstractCollection
from copy import copy


class Tool(AbstractItem):
    """Concept denoting any tool that the player can produce."""

    @classmethod
    def from_dict(cls, name, data):
        tool = super(Tool, cls).from_dict(name, data)
        tool.durability = data.get("durability", -1)
        tool.mining_bonus = data.get("mining_bonus", {})
        tool.crafting_bonus = data.get("crafting_bonus", {})
        tool.research_bonus = data.get("research_bonus", 0)
        tool.condition = tool.durability
        return tool

    def serialize(self):
        """Serialize into dict."""
        return {
            "name": self.name,
            "condition": self.condition,
        }

    def __repr__(self):
        """Representation, e.g. 'clay_shovel (worn)'"""
        if self.durability == -1 or self.durability == self.condition:
            return "${}$".format(self.name)

        wear = 1.0 * self.condition / self.durability
        descriptions = {
            1: "new",
            .9: "slightly used",
            .8: "used",
            .6: "worn",
            .3: "damaged",
            .15: "about to break",
        }
        for thresh, des in sorted(descriptions.items()):
            if wear < thresh:
                return "${}$ ({})".format(self.name, des)


class Tools(AbstractCollection):
    FIXTURES = "items.yaml"
    ITEM_CLASS = Tool

    def craft(self, item):
        return copy(item)

    def instantiate(self, data):
        item = self.get(data['name'])
        copy = self.craft(item)
        copy.condition = data.get('condition')
        return copy

    def is_available(self, item_name):
        item = self.get(item_name)
        return item.name in self.game.flags.items_enabled or super(Tools, self).is_available(item)
