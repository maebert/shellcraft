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

    tutorial_step = 0

    resource_enabled = {
        "clay": True,
        "ore": False,
        "flint": False
    }

    commands_enabled = ['reset']

    items_enabled = []
    research_completed = []

    mining_difficulty = {
        "clay": 1,
        "ore": 1,
        "flint": 1
    }

    mining_difficulty_increment = {
        "clay": .5,
        "ore": .5,
        "flint": .5
    }


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
        return self._can_afford(required_resources=cost)

    def _resources_missing_to_craft(self, item_name):
        cost = ToolBox.get_cost(item_name)
        return {res: res_cost - self.resources.get(res) for res, res_cost in cost.items() if res_cost - self.resources.get(res) > 0}

    def _craft(self, item_name):
        cost = ToolBox.get_cost(item_name)
        for resource, res_cost in cost.items():
            self.resources.add(resource, -res_cost)
        self._create_item(item_name)
        self._messages.append("Crafted ${}$".format(item_name))

    def _best_mining_tool(self, resource):
        """Return the (currently owned) tool that gives the highest bonus on mining a particular resource."""
        bonus, item = max((item.mining_bonus.get(resource, 0), item) for item in self.items)
        return item

    def _get_item(self, item_name):
        """Return the first item that matches the name or None."""
        for item in self.items:
            if item.name == item_name:
                return item

    def _can_afford(self, **cost):
        if 'resources_required' in cost and not all(self.resources.get(res) >= res_cost for res, res_cost in cost['resources_required'].items()):
            return False
        if 'items_required' in cost and not all(map(self.get_item, cost['items_required'])):
            return False

        research_required = cost.get('research_required', [])
        if isinstance(research_required, (tuple, list)) and not set(research_required).issubset(self.flags.research_completed):
            return False
        elif isinstance(research_required, str) and research_required not in self.flags.research_completed:
            return False

        enabled_items = cost.get('enabled_items', [])
        if isinstance(enabled_items, (tuple, list)) and not set(enabled_items).issubset(self.flags.items_enabled):
            return False
        elif isinstance(enabled_items, str) and research_required not in self.flags.items_enabled:
            return False

        return True

    def _unlock_items(self):
        for item in ToolBox.tools.values():
            if item.name != 'item' and item.name not in self.flags.items_enabled and self._can_afford(**item.prerequisites):
                self._messages.append("Unlocked ${}$.".format(item.name))
                self.flags.items_enabled.append(item.name)

    def mine(self, resource):
        """Mine a resource."""
        if self.is_busy:
            return None  # @Todo Raise Exception

        difficulty = self.flags.mining_difficulty.get(resource)

        total_wear = 0
        efficiency = 0

        while self.items and total_wear < difficulty:
            tool = self._best_mining_tool(resource)
            if tool.condition <= (difficulty - total_wear):
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

        self.flags.mining_difficulty[resource] = self.flags.mining_difficulty[resource] + self.flags.mining_difficulty_increment[resource]
        self._act("mine", resource, difficulty)
        self.resources.add(resource, efficiency)
        self._unlock_items()
        self._messages.append("Mined *{} {}*.".format(efficiency, resource))
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
