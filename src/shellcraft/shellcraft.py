# -*- coding: utf-8 -*-
"""Game Classes."""

from __future__ import absolute_import, division, print_function, unicode_literals

from shellcraft.tools import ToolFactory
from shellcraft.research import ResearchFactory
from shellcraft.tutorial import TutorialFactory
from shellcraft.events import EventFactory
from shellcraft.missions import MissionFactory
from shellcraft.fractions import FractionProxy
from shellcraft.grammar import VERBS

from shellcraft.game_state_pb2 import GameState
from google.protobuf import json_format
from shellcraft.core import ResourceProxy, ItemProxy

from random import random
import os
import datetime


class ShellcraftException(RuntimeError):
    pass


class BusyException(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""
    def __init__(self, game):
        self._time_left = game.state.action.completion.ToDatetime() - datetime.datetime.now()
        self._action = game.state.action.task

    def __str__(self):
        return "You're busy {} for another {:.0f} seconds.".format(VERBS[self._action], self._time_left.total_seconds())


class ResourceNotAvailable(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""
    def __init__(self, resource):
        self._resource = resource

    def __str__(self):
        return "You can't mine {} yet".format(self._resource)


class Game(object):
    """The Game class holds all information about, well, the game's state, and handles the logic."""

    def __init__(self, state=None):
        """Create a new Game instante."""
        self.state = state or GameState()

        self._messages = []

        self.lab = ResearchFactory(self)
        self.workshop = ToolFactory(self)
        self.tutorial = TutorialFactory(self)
        self.events = EventFactory(self)
        self.mission_factory = MissionFactory(self)

        self.resources = ResourceProxy(self.state.resources)
        self.total_mined = ResourceProxy(self.state.stats.total_mined)

        self.mining_difficulty = ResourceProxy(self.state.mining_difficulty)
        self.mining_difficulty_increment = ResourceProxy(self.state.mining_difficulty_increment)

        self.tools = ItemProxy(self.state.tools, self.workshop)
        self.missions = ItemProxy(self.state.missions, self.mission_factory)
        self.fractions = FractionProxy(self.state.fractions)

        self.save_file = None

    def alert(self, msg, *args):
        """Add a message to the alert stack."""
        self._messages.append(msg.format(*args))

    @property
    def is_busy(self):
        """True if the player is currently mining or crafting."""
        if self.state.action.task:
            if datetime.datetime.now() > self.state.action.completion.ToDatetime():
                self.state.action.Clear()
                return False
            return True
        return False

    def add_mission(self, mission):
        """Add a new mission.

        Args:
            mission (str): Mission template to use.
        """
        mission = self.missions.add(mission)
        if not mission.offer(self):
            self.missions.remove(mission)

    def complete_missions(self):
        """Check if any missions can be completed."""
        for mission in self.missions:
            if mission.is_completed(self):
                self.missions.remove(mission)

    def craft(self, tool_name):
        """Craft a new tool by expending resources and time."""
        item = self.workshop.get(tool_name)
        for resource, res_cost in item.cost.items():
            self.resources.add(resource, -res_cost)
        self.tools.add(item)
        self._act("craft", tool_name, item.difficulty)
        self.alert("Crafted {}", item)
        return item.difficulty

    def research(self, project_name):
        """Research a new project by expending time."""
        project = self.lab.get(project_name)
        self.state.research_completed.append(project.name)
        self._act("research", project_name, project.difficulty)
        self.alert("Researched {}.", project)
        self.lab.apply_effects(project)
        return project.difficulty

    def has_item(self, item_name):
        """True if the player has an instance of the tool in posession."""
        for item in self.tools:
            if item.name == item_name:
                return True
        return False

    def _best_mining_tool(self, resource):
        """Return the (currently owned) tool that gives the highest bonus on mining a particular resource."""
        if self.tools.is_empty:
            return None
        return max(self.tools, key=lambda item: item.mining_bonus.get(resource, 0))

    def mine(self, resource):
        """Mine a resource."""
        if self.is_busy:
            raise BusyException(self)

        difficulty = self.mining_difficulty.get(resource)

        total_wear = 0
        efficiency = 0
        events = []

        while not self.tools.is_empty and total_wear < difficulty:
            tool = self._best_mining_tool(resource)
            if tool.condition <= (difficulty - total_wear):
                contribution = tool.condition / difficulty
                total_wear += tool.condition
                efficiency += tool.condition * tool.mining_bonus.get(resource, 1) / difficulty
                self.alert("Destroyed ${}$ while mining *{}*.".format(tool.name, resource))
                self.tools.remove(tool)
            else:
                contribution = (difficulty - total_wear) / difficulty
                tool.condition -= (difficulty - total_wear)
                total_wear = difficulty

            efficiency += contribution * tool.mining_bonus.get(resource, 1)

            for event, prob in tool.event_bonus.items():
                if random() * contribution < prob:
                    events.append(event)

        # Hand mining has efficiency of 1
        efficiency += (difficulty - total_wear) / difficulty

        # Can only ever get integer results
        efficiency = int(efficiency)

        self.mining_difficulty.add(resource, self.mining_difficulty_increment.get(resource))

        self._act("mine", resource, difficulty)
        self.resources.add(resource, efficiency)

        self.total_mined.add(resource, efficiency)

        self._unlock_items()
        self.alert("Mined *{} {}*.".format(efficiency, resource))
        self.events.trigger(*events)
        return difficulty, efficiency

    def _unlock_items(self):
        for item in self.workshop.available_items:
            if item.name not in self.state.tools_enabled:
                self.alert("You can now craft {}.", item)
                self.state.tools_enabled.append(item.name)

        for item in self.lab.available_items:
            if item.name not in self.state.research_enabled:
                self.alert("You can now research %{}%.", item.name)
                self.state.research_enabled.append(item.name)

    def _act(self, task, target, duration):
        if self.is_busy:
            raise BusyException(self)

        self.state.stats.total_game_duration += duration
        if self.state.debug:
            duration = 0
        self.state.action.task = task
        self.state.action.target = str(target)
        self.state.action.completion.FromDatetime(datetime.datetime.now() + datetime.timedelta(seconds=duration))

    @classmethod
    def load(cls, filename):
        """Load a game from a save file."""
        with open(filename) as f:
            state = json_format.Parse(f.read(), GameState())
            game = cls(state)
            game.save_file = filename
        return game

    @classmethod
    def create(cls, filename):
        """Create a new game."""
        game = Game()

        game.state.mining_difficulty.clay = .5
        game.state.mining_difficulty.ore = .5
        game.state.mining_difficulty.energy = .5
        game.state.mining_difficulty_increment.clay = .5
        game.state.mining_difficulty_increment.ore = .5
        game.state.mining_difficulty_increment.energy = .5

        game.save_file = filename
        save_path, _ = os.path.split(filename)
        if save_path and not os.path.exists(save_path):
            os.makedirs(save_path)
        game.save()
        return game

    def save(self, filename=None):
        """Save a game to disk."""
        with open(filename or self.save_file, 'w') as f:
            f.write(json_format.MessageToJson(self.state))
