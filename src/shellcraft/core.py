# -*- coding: utf-8 -*-
"""Core Classes."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import yaml
from copy import copy
from shellcraft.utils import to_list, to_float

RESOURCES = ['clay', 'energy', 'ore']


class ResourceProxy(object):
    """Countable Resources."""

    def __init__(self, field):
        self._resources = field

    def add(self, resource, value):
        """Add resource."""
        setattr(self._resources, resource, getattr(self._resources, resource, 0) + value)

    def get(self, resource, default=0):
        """Get value of resource."""
        return getattr(self._resources, resource, default)

    def multiply(self, resource, factor):
        """Multiply resource by factor."""
        setattr(self._resources, resource, getattr(self._resources, resource, 0) * factor)


class ItemProxy(object):
    def __init__(self, field, factory):
        self._field = field
        self._factory = factory
        self._items = [factory.make(pb) for pb in field]

    def __iter__(self):
        return self._items.__iter__()

    def remove(self, item):
        self._items.remove(item)
        self._field.remove(item._pb)

    def __bool__(self):
        return bool(self._items)

    def add(self, item):
        pb = self._field.add()
        new_item = self._factory.make(item)
        for field in self._factory.PB_CLASS.DESCRIPTOR.fields_by_name.keys():
            if hasattr(new_item, field):
                setattr(pb, field, getattr(new_item, field))
        new_item._pb = pb
        self._items.append(new_item)
        return new_item


class BaseItem(object):
    _pb = None

    def __init__(self, name):
        self.name = name
        self.difficulty = 0
        self.description = ""
        self.prerequisites = {}
        self.cost = {}
        self.effects = {}
        self.strings = {}

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
        item.strings = data.get("strings", {})
        item.effects = data.get("effects", {})
        for effect in ('enable_commands', 'enable_items', 'enable_resources', 'events'):
            item.effects[effect] = to_list(item.effects.get(effect))
        return item

    def __repr__(self):
        return self.name

    def __setattr__(self, key, value):
        if key != "_pb" and self._pb and key in self._pb.__class__.DESCRIPTOR.fields_by_name.keys():
            setattr(self._pb, key, value)
        else:
            self.__dict__[key] = value

    def __getattr__(self, key):
        if key != "_pb" and self._pb and key in self._pb.__class__.DESCRIPTOR.fields_by_name.keys():
            return getattr(self._pb, key)
        raise AttributeError(key)


class BaseFactory(object):
    FIXTURES = "collection.yaml"
    ITEM_CLASS = BaseItem
    PB_CLASS = None

    def __init__(self, game):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", self.FIXTURES)) as f:
            self.all_items = {name: self.ITEM_CLASS.from_dict(name, data) for name, data in yaml.load(f).items()}
        self.game = game

    def get(self, item_name):
        """Get an item instance by name."""
        if isinstance(item_name, BaseItem):
            return item_name
        return self.all_items.get(item_name)

    def make(self, source):
        if isinstance(source, str):
            return copy(self.get(source))
        elif self.PB_CLASS and isinstance(source, self.PB_CLASS):
            item = copy(self.get(source.name))
            item._pb = source
            return item
        else:
            return copy(source)

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

        # Enable commands
        for command in item.effects.get('enable_commands', []):
            if command not in self.game.state.commands_enabled:
                self.game.alert("You unlocked the `{}` command", command)
                self.game.state.commands_enabled.append(command)

        # Enable resouces
        for resources in item.effects.get('enable_resources', []):
            if resources not in self.game.state.resources_enabled:
                self.game.alert("You can now mine ${}$.", resources)
                self.game.state.resources_enabled.append(resources)

        # Enable items
        for item_name in item.effects.get('enable_items', []):
            if item_name not in self.game.state.tools_enabled:
                self.game.alert("You can now craft ${}$.", item_name)
                self.game.state.tools_enabled.append(item_name)

        # Enable research
        for item_name in item.effects.get('enable_research', []):
            if item_name not in self.game.state.research_enabled:
                self.game.alert("You can now research @{}@.", item_name)
                self.game.state.research_enabled.append(item_name)

        # Grant resources
        for resource in RESOURCES:
            if resource in item.effects:
                value = to_float(item.effects[resource])
                self.game.resources.add(resource, value)
                if value > 0:
                    self.game.alert("You found *{} {}*.", value, resource)
                else:
                    self.game.alert("You lost *{} {}*.", value, resource)

        # Change mining difficulty
        for resource in RESOURCES:
            change = item.effects.get("{}_mining_difficulty".format(resource), None)
            if change:
                change = to_float(change)
                self.game.mining_difficulty.multiply(resource, 1 - change)
                self.game.alert("*{}* difficulty reduced by {:.0%}.", resource, change)

        # Trigger events
        self.game.events.trigger(*item.effects.get('events', []))

    def is_available(self, item_name):
        """Return true if the prerequisites for an item are met."""
        item = self.get(item_name)
        if not item:
            return False
        for resource in RESOURCES:
            if self.game.resources.get(resource) < item.prerequisites.get(resource, 0):
                return False
        for required_item in item.prerequisites['items']:
            if not self.game.has_item(required_item):
                return False
        for research in item.prerequisites['research']:
            if research not in self.game.state.research_completed:
                return False
        return True
