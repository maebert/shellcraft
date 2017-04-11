# -*- coding: utf-8 -*-
"""Game Classes."""

from __future__ import absolute_import

from shellcraft.core import StateCollector
from shellcraft.items import Tools
from shellcraft.research import Research
from shellcraft.tutorial import Tutorial
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

    debug = False

    resources_enabled = ['clay']
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


class Game(object):
    """The Game class holds all information about, well, the game's state, and handles the logic."""

    def __init__(self):
        """Create a new Game instante."""
        self.resources = Resources()
        self.flags = Flags()
        self.items = []
        self.action = Action()
        self._messages = []

        self.lab = Research(self)
        self.tools = Tools(self)
        self.tutorial = Tutorial(self)

    def alert(self, msg, *args):
        self._messages.append(msg.format(*args))

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

    def craft(self, item_name):
        item = self.tools.get(item_name)
        for resource, res_cost in item.cost.items():
            self.resources.add(resource, -res_cost)
        self.items.append(self.tools.craft(item))
        self._act("craft", item_name, item.difficulty)
        self.alert("Crafted {}", item)
        return item.difficulty

    def research(self, project_name):
        project = self.lab.get(project_name)
        self.flags.research_completed.append(project.name)
        self._act("research", project_name, project.difficulty)
        self.alert("Researched {}.", project)
        self.lab.apply_effects(project)
        return project.difficulty

    def _best_mining_tool(self, resource):
        """Return the (currently owned) tool that gives the highest bonus on mining a particular resource."""
        return max(self.items, key=lambda item: item.mining_bonus.get(resource, 0))

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
                efficiency += tool.condition * tool.mining_bonus.get(resource) / difficulty
                self.alert("Destroyed ${}$ while mining *{}*.".format(tool.name, resource))
                self.items.remove(tool)
            else:
                tool.condition -= (difficulty - total_wear)
                efficiency += (difficulty - total_wear) * tool.mining_bonus.get(resource) / difficulty
                total_wear = difficulty

        # Hand mining has efficiency of 1
        efficiency += (difficulty - total_wear) / difficulty

        self.flags.mining_difficulty[resource] = self.flags.mining_difficulty[resource] + self.flags.mining_difficulty_increment[resource]
        self._act("mine", resource, difficulty)
        self.resources.add(resource, efficiency)
        self._unlock_items()
        self.alert("Mined *{} {}*.".format(efficiency, resource))
        return difficulty, efficiency

    def _unlock_items(self):
        for item in self.tools.available_items:
            if item.name not in self.flags.items_enabled:
                self.alert("You can now craft the {}.", item)
                self.flags.items_enabled.append(item.name)

    def _act(self, task, target, duration):
        if self.is_busy:
            return None  # @Todo Raise Exception
        if self.flags.debug:
            duration = 0
        self.action.task = task
        self.action.target = str(target)
        self.action.completion = to_date(duration)

    def to_dict(self):
        """Serialize to dict."""
        return {
            "resources": self.resources.to_dict(),
            "action": self.action.to_dict(),
            "flags": self.flags.to_dict(),
            "items": [item.serialize() for item in self.items]
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
        game = cls()
        game.resources = Resources.from_dict(d.get('resources', {}))
        game.action = Action.from_dict(d.get('action', {}))
        game.flags = Flags.from_dict(d.get('flags', {}))
        game.items = [game.tools.instantiate(item) for item in d.get('items', [])]
        return game
