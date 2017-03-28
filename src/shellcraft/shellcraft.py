# -*- coding: utf-8 -*-
"""Game Classes."""

from __future__ import absolute_import

from shellcraft.core import StateCollector, ToolBox
import shellcraft.items  # noqa
import json
import os


class Resources(StateCollector):
    """Countable Resources."""

    ore = 0
    clay = 0
    energy = 0


class Flags(StateCollector):
    """Flags that get set during the game."""

    tutorial_1 = False
    clay_available = True
    ore_available = True
    energy_available = False

    def resource_available(self, resource):
        """Check if a resource is available for mining."""
        return self.__dict__.get("{}_available".format(resource))


class Game:
    """The Game class holds all information about, well, the game's state, and handles the logic."""

    def __init__(self, resources=None, flags=None, items=None):
        """Create a new Game instante."""
        self.resources = resources or Resources()
        self.flags = flags or Flags()
        self.items = items or []

    def _create_item(self, name, **attrs):
        item = ToolBox.get(name, **attrs)
        self.items.append(item)
        return item

    def _can_craft(self, item_name):
        cost = ToolBox.get_cost(item_name)
        return all(self.resources.get(res) >= res_cost for res, res_cost in cost.items())

    def _resources_missing_to_craft(self, item_name):
        cost = ToolBox.get_cost(item_name)
        return {res: res_cost - self.resources.get(res) for res, res_cost in cost.items() if res_cost - self.resources.get(res) > 0}

    def _craft(self, item_name):
        cost = ToolBox.get_cost(item_name)
        for resource, res_cost in cost.items():
            self.resources.add(resource, -res_cost)
        self._create_item(item_name)

    def _best_mining_tool(self, resource):
        """Return the (currently owned) tool that gives the highest bonus on mining a particular resource."""
        bonus, item = max((item.mining_bonus.get(resource, 0), item) for item in self.items)
        return item

    def to_dict(self):
        """Serialize to dict."""
        return {
            "resources": self.resources.to_dict(),
            "flags": self.flags.to_dict(),
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def load(cls, filename):
        """Load a game from a save file."""
        with open(filename) as f:
            data = json.load(f)
            game = cls.from_dict(data)
            game.save_file = filename
        return game

    @classmethod
    def create(cls, filename):
        """Create a new game."""
        game = Game()
        game.save_file = filename
        save_path, _ = os.path.split(filename)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        game.save()
        return game

    def save(self):
        """Save a game to disk."""
        with open(self.save_file, 'w') as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def from_dict(cls, d):
        """Deserialize from dict."""
        resources = Resources.from_dict(d.get('resources', {}))
        flags = Flags.from_dict(d.get('flags', {}))
        items = [ToolBox.get(**item) for item in d.get('items', [])]
        return cls(resources=resources, flags=flags, items=items)
