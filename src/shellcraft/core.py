# -*- coding: utf-8 -*-
"""Core Classes."""

import inflection


class StateCollector:
    """Class that acts as a serializable accessor to game state variables."""

    def __init__(self):
        """Create a new StateCollector."""
        self.__dict__.update({k: v for k, v in self.__class__.__dict__.items() if not k.startswith("_") and isinstance(v, (str, int, float, bool))})

    def to_dict(self):
        """Create a serializable dict representing this state."""
        return self.__dict__

    def get(self, key):
        """Get the value for a key programatically."""
        return self.__dict__.get(key)

    def add(self, key, value):
        """Add to the value of a key programatically."""
        self.__dict__[key] += value

    @classmethod
    def from_dict(cls, d):
        """Deserialise from a dict."""
        state = cls()
        state.__dict__.update(d)
        return state


class ToolBox(type):
    """Meta class that acts as a item registry."""

    tools = {}

    @classmethod
    def get(cls, name, **kwargs):
        """Instantiate a new item from the toolbox by name.

        Example:
            >>> ToolBox.get("clay_shovel", condition=.4)
        """
        if name not in cls.tools:
            raise ValueError
        else:
            tool_cls = cls.tools.get(name)
            return tool_cls(**kwargs)

    @classmethod
    def get_cost(cls, name):
        """Return the cost of any item.

        Example:
            >>> ToolBox.get_cost("clay_shovel")
            {"clay": 6}
        """
        if name not in cls.tools:
            raise ValueError
        else:
            return cls.tools.get(name).cost

    def __new__(meta, class_name, bases, class_dict):  # noqa
        """Create a new (Item) class and register it in the ToolBox."""
        cls = type.__new__(meta, class_name, bases, class_dict)
        cls.name = inflection.underscore(cls.__name__)
        ToolBox.tools[cls.name] = cls
        return cls


class Item(metaclass=ToolBox):  # noqa
    """Concept denoting any tool that the player can produce."""

    __metaclass__ = ToolBox

    durability = 1
    mining_bonus = {}
    crafting_bonus = {}

    def __init__(self, condition=None):
        """Create a new instance of the item.

        Usually called because it gets added to the game state when a
        player crafts this item, or when we load a saved game state.
        """
        self.condition = condition or self.durability

    def to_dict(self):
        """Serialize into dict."""
        return {
            "name": self.name,
            "condition": self.condition,
        }

    def __repr__(self):
        """Representation, e.g. 'clay_shovel (82%)'"""
        return "{} ({:.0%})".format(self.name, 1.0 * self.condition / self.durability)
