# -*- coding: utf-8 -*-
"""Core Classes."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import yaml
from copy import copy
from shellcraft.utils import to_list, to_float
from google.protobuf.descriptor import Descriptor
from builtins import str

RESOURCES = ['clay', 'energy', 'ore']


class ResourceProxy(object):
    """Proxy for accessing Resource messages in a GameState."""

    def __init__(self, field):
        """Initialise the Proxy.

        Args:
            field (shellcraft.game_state_pb2.Resources): Resource message.
        """
        self._resources = field

    @property
    def _fields(self):
        return self._resources.__class__.DESCRIPTOR.fields_by_name.keys()

    def add(self, resource, value):
        """Add resource.

        Args:
            resource (str)
            value (float)
        """
        setattr(self._resources, resource, getattr(self._resources, resource, 0) + value)

    def get(self, resource, default=0):
        """Get value of resource."""
        return getattr(self._resources, resource, default)

    def multiply(self, resource, factor):
        """Multiply resource by factor."""
        setattr(self._resources, resource, getattr(self._resources, resource, 0) * factor)

    def __repr__(self):
        """String representation of resources."""
        return str({f: self.get(f) for f in self._fields})


class ItemProxy(object):
    """Proxy for accessing serializable items."""

    def __init__(self, field, factory):
        """Initialise the Proxy.

        Args:
            field: Message of 'Repeated' type
            factory (shellcraft.core.BaseFactory): Factory used to produce the item.
        """
        self._field = field
        self._factory = factory
        self._items = [factory.make(pb) for pb in field]

    def __iter__(self):
        """Iterate over items."""
        return self._items.__iter__()

    def remove(self, item):
        """Remove an item."""
        self._items.remove(item)
        self._field.remove(item._pb)

    def __bool__(self):
        """True if the proxy contains any items."""
        return bool(self._items)

    @property
    def is_empty(self):
        """True if the proxy does not contain any items."""
        return not self._items

    def __repr__(self):
        """String representation of item proxy."""
        return str(self._items)

    def add(self, item):
        """Add a new item.

        This is achieved by first adding a Protobuf message to the field,
        then using the factory to make a new item from a given template,
        setting all fields on the Protobuf message and attaching it to the
        newly generated item.

        Args:
            item: Item name or Item instance to copy from
        """
        pb = self._field.add()
        new_item = self._factory.make(item)
        for field in self._factory.PB_CLASS.DESCRIPTOR.fields_by_name.keys():
            if hasattr(new_item, field):
                if isinstance(self._factory.PB_CLASS.DESCRIPTOR.fields_by_name[field].message_type, Descriptor):
                    getattr(pb, field).CopyFrom(getattr(new_item, field))
                else:
                    setattr(pb, field, getattr(new_item, field))
        new_item._pb = pb
        self._items.append(new_item)
        return new_item


class BaseItem(object):
    """Abstract class for new items."""

    _pb = None
    """This links the item to a serializable Protobuf message that is part of the GameState."""

    def __init__(self, name):
        """Initialise an empty item."""
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
        """String representation of the item."""
        return self.name

    def __setattr__(self, key, value):
        """Override attribute setter for items with attached Protobuf message."""
        if key != "_pb" and self._pb and key in self._pb.__class__.DESCRIPTOR.fields_by_name.keys():
            setattr(self._pb, key, value)
        else:
            self.__dict__[key] = value

    def __getattr__(self, key):
        """Override attribute getter for items with attached Protobuf message."""
        if key != "_pb" and self._pb and key in self._pb.__class__.DESCRIPTOR.fields_by_name.keys():
            return getattr(self._pb, key)
        raise AttributeError(key)


class BaseFactory(object):
    """Factory pattern to instantiate items."""

    FIXTURES = "collection.yaml"
    ITEM_CLASS = BaseItem
    PB_CLASS = None

    def __init__(self, game):
        """Initialise the Factory.

        Args:
            game (shellcraft.shellcraft.Game): Game object.
        """
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", self.FIXTURES)) as f:
            self.all_items = {name: self.ITEM_CLASS.from_dict(name, data) for name, data in yaml.load(f).items()}
        self.game = game

    def get(self, item_name):
        """Get an item instance by name."""
        if isinstance(item_name, BaseItem):
            return item_name
        return self.all_items.get(item_name)

    def make(self, source):
        """Create a new unique item from a source.

        The source may be a string, in which case the item is created from
        the item library defined in a YAML file, or it may be a Protobuf message,
        which is typically the case when loading a saved game and instantiating
        serialized items (such as tools or missions), or it may be another Item
        instance which will be copied.
        """
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
        return {res: int(res_cost - self.game.resources.get(res)) for res, res_cost in item.cost.items() if res_cost - self.game.resources.get(res) > 0}

    def can_afford(self, item_name):
        """Return true if we have enough resources to create an item."""
        item = self.get(item_name)
        for resource in RESOURCES:
            if item.cost.get(resource, 0) > self.game.resources.get(resource):
                return False

        return True

    def apply_effects(self, item_name):
        """Apply all effects of an item."""
        item = self.get(item_name)

        # Enable commands
        for command in item.effects.get('enable_commands', []):
            if command not in self.game.state.commands_enabled:
                self.game.alert("You unlocked the `{}` command", command)
                self.game.state.commands_enabled.append(command)

        # Enable resouces
        for resources in item.effects.get('enable_resources', []):
            if resources not in self.game.state.resources_enabled:
                self.game.alert("You can now mine *{}*.", resources)
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
                self.game.alert("*{}* mining difficulty reduced by {:.0%}.", resource, change)

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
