# -*- coding: utf-8 -*-
"""Game Classes."""

from __future__ import absolute_import

from shellcraft.core import StateCollector, ToolBox
import shellcraft.items  # noqa
import json
import os
import datetime


def to_date(delta_seconds):
    return (datetime.datetime.now() + datetime.timedelta(seconds=delta_seconds)).isoformat()


def parse_isoformat(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")


class Resources(StateCollector):
    """Countable Resources."""

    ore = 0
    clay = 0
    energy = 0

    def add(self, resource, value):
        """Add resource."""
        self.__dict__[resource] += value


class Flags(StateCollector):
    """Flags that get set during the game."""

    tutorial_1 = False
    clay_available = True
    ore_available = True
    energy_available = False

    clay_difficulty = 1
    ore_difficulty = 1
    energy_difficulty = 1

    def resource_available(self, resource):
        """Check if a resource is available for mining."""
        return self.__dict__.get("{}_available".format(resource))

    def resource_difficulty(self, resource):
        """Return the difficulty of mining a resource."""
        return self.__dict__.get("{}_difficulty".format(resource))

    def raise_resource_difficulty(self, resource, value=.5):
        """Set the difficulty of mining a resource."""
        self.__dict__["{}_difficulty".format(resource)] += value


class Action(StateCollector):
    """Information about the current action."""

    task = None
    target = None
    completion = None


class Game:
    """The Game class holds all information about, well, the game's state, and handles the logic."""

    def __init__(self, resources=None, flags=None, items=None, action=None):
        """Create a new Game instante."""
        self.resources = resources or Resources()
        self.flags = flags or Flags()
        self.items = items or []
        self.action = action or Action()
        self._messages = []

    @property
    def is_busy(self):
        """True if the player is currently mining or crafting."""
        if self.action.task:
            if datetime.datetime.now() > parse_isoformat(self.action.completion):
                self.action.task = None
                self.action.completion = None
                self.action.target = None
                return False
            return True
        return False

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

    def mine(self, resource):
        """Mine a resource."""
        if self.is_busy:
            return None  # @Todo Raise Exception

        difficulty = self.flags.resource_difficulty(resource)

        total_wear = 0
        efficiency = 0

        while self.items and total_wear < difficulty:
            tool = self._best_mining_tool(resource)
            if tool.condition < (difficulty - total_wear):
                total_wear += tool.condition
                efficiency += tool.condition * tool.mining_bonus[resource] / difficulty
                self._messages.append("Destroyed ${}$ while mining *{}*.".format(tool.name, resource))
                self.items.remove(tool)
            else:
                tool.condition -= (difficulty - total_wear)
                efficiency += (difficulty - total_wear) * tool.mining_bonus[resource] / difficulty
                total_wear = difficulty

        # Hand mining has efficiency of 1
        efficiency += (difficulty - total_wear) / difficulty

        self.flags.raise_resource_difficulty(resource)
        self._act("mine", resource, difficulty)
        self.resources.add(resource, efficiency)
        return difficulty, efficiency

    def _act(self, task, target, duration):
        if self.is_busy:
            return None  # @Todo Raise Exception
        self.action.task = task
        self.action.target = target
        self.action.completion = to_date(duration)

    def to_dict(self):
        """Serialize to dict."""
        return {
            "resources": self.resources.to_dict(),
            "action": self.action.to_dict(),
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
        action = Action.from_dict(d.get('action', {}))
        flags = Flags.from_dict(d.get('flags', {}))
        items = [ToolBox.get(**item) for item in d.get('items', [])]
        return cls(resources=resources, flags=flags, items=items, action=action)
