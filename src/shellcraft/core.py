# -*- coding: utf-8 -*-
"""Core Classes."""

import os
import yaml

RESOURCES = ['clay', 'energy', 'ore']


def to_list(string_or_list):
    """Encapsulate strings or numbers in a list."""
    if not string_or_list:
        return []
    if not isinstance(string_or_list, (list, tuple)):
        return [string_or_list]
    return string_or_list


class StateCollector(object):
    """Class that acts as a serializable accessor to game state variables."""

    def __init__(self):
        """Create a new StateCollector."""
        self.__dict__.update({k: v for k, v in self.__class__.__dict__.items() if not k.startswith("_") and isinstance(v, (str, int, float, bool, list, dict))})

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


class AbstractItem(object):
    def __init__(self, name):
        self.name = name
        self.difficulty = 0
        self.description = ""
        self.prerequisites = {}
        self.cost = {}
        self.effects = {}

    @classmethod
    def from_dict(cls, name, data):
        """Load an item from dict representation."""
        item = cls(name)

        item.description = data.get("description", "")
        item.difficulty = data.get("difficulty", 0)

        item.prerequisites = data.get("prerequisites", {})
        item.prerequisites['items'] = to_list(item.prerequisites.get('items'))
        item.prerequisites['research'] = to_list(item.prerequisites.get('research'))
        item.cost = data.get("cost", {})
        item.effects = data.get("effects", {})
        for effect in ('enable_commands', 'enable_items', 'enable_resources'):
            item.effects[effect] = to_list(item.effects.get(effect))
        return item

    def serialize(self):
        """Serialise the AbstractItem."""
        return self.name

    def __repr__(self):
        return self.name


class AbstractCollection(object):
    FIXTURES = "collection.yaml"
    ITEM_CLASS = AbstractItem

    def __init__(self, game):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", self.FIXTURES)) as f:
            self.all_items = {name: self.ITEM_CLASS.from_dict(name, data) for name, data in yaml.load(f).items()}
        self.game = game

    def get(self, item_name):
        """Get an item instance by name."""
        if isinstance(item_name, AbstractItem):
            return item_name
        return self.all_items.get(item_name)

    @property
    def available_items(self):
        """Return all items that are currently available."""
        return [item for item in self.all_items.values() if self.is_available(item)]

    def _resources_missing_to_craft(self, item_name):
        item = self.get(item_name)
        return {res: res_cost - self.game.resources.get(res) for res, res_cost in item.cost.items() if res_cost - self.game.resources.get(res) > 0}

    def can_afford(self, item_name):
        """Return true if we have enough resources to create an item."""
        item = self.get(item_name)
        for resource in RESOURCES:
            if item.cost.get(resource, 0) > self.game.resources.get(resource):
                return False

        return True

    def apply_effects(self, item_name):
        item = self.get(item_name)
        for command in item.effects.get('enable_commands', []):
            if command not in self.game.flags.commands_enabled:
                self.game.alert("You unlocked the `{}` command".format(command))
                self.game.flags.commands_enabled.append(command)
        for resources in item.effects.get('enable_resourcess', []):
            if resources not in self.game.flags.resourcess_enabled:
                self.game.alert("You discovered ${}$.".format(resources))
                self.game.flags.resources_enabled.append(resources)
        for item_name in item.effects.get('enable_items', []):
            if item_name not in self.game.flags.items_enabled:
                self.game.alert("You can now craft the ${}$.".format(item_name))
                self.game.flags.items_enabled.append(item_name)

    def is_available(self, item_name):
        """Return true if the prerequisites for an item are met."""
        item = self.get(item_name)
        if not item:
            return False
        for resource in RESOURCES:
            if self.game.resources.get(resource) < item.prerequisites.get(resource, 0):
                return False
        for required_item in item.prerequisites['items']:
            if not self.game.tools.get(required_item):
                return False
        for research in item.prerequisites['research']:
            if research not in self.game.flags.research_completed:
                return False
        return True
