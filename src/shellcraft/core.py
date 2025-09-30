# -*- coding: utf-8 -*-
"""Core Classes."""

import os
from builtins import str
from copy import copy
from typing import Any, Dict, List, Optional, Union

import toml
from pydantic import BaseModel, Field, root_validator

from shellcraft.utils import to_float, to_list

RESOURCES = ["clay", "energy", "ore"]


class ResourceProxy(object):
    """Proxy for accessing Resource messages in a GameState."""

    def __init__(self, field):
        """Initialise the Proxy.

        Args:
            field (shellcraft.game_state.Resources): Resource message.
        """
        self._resources = field

    @property
    def _fields(self):
        return ["clay", "ore", "energy"]

    def add(self, resource, value):
        """Add resource.

        Args:
            resource (str)
            value (float)
        """
        setattr(
            self._resources, resource, getattr(self._resources, resource, 0) + value
        )

    def get(self, resource, default=0):
        """Get value of resource."""
        return getattr(self._resources, resource, default)

    def multiply(self, resource, factor):
        """Multiply resource by factor."""
        setattr(
            self._resources, resource, getattr(self._resources, resource, 0) * factor
        )

    def __repr__(self):
        """String representation of resources."""
        return str({f: self.get(f) for f in self._fields})


class ItemProxy(object):
    """Proxy for accessing serializable items."""

    def __init__(self, field, factory, filter=None):
        """Initialise the Proxy.

        Args:
            field: Message of 'Repeated' type
            factory (shellcraft.core.BaseFactory): Factory used to produce the item.
        """
        self._field = field
        self._factory = factory
        self._items = [factory.make(pb) for pb in field]
        self.filter = filter

    @property
    def _filtered_items(self):
        return filter(self.filter, self._items)

    def __iter__(self):
        """Iterate over items."""
        return self._filtered_items.__iter__()

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
        return not list(self._filtered_items)

    def __repr__(self):
        """String representation of item proxy."""
        return str(self._filtered_items)

    def add(self, item):
        """Add a new item.

        This creates a new Pydantic model instance and adds it to the field,
        then creates a corresponding game item instance.

        Args:
            item: Item name or Item instance to copy from
        """
        # Create a new Pydantic model instance for serialization
        pb = self._field.add()
        new_item = self._factory.make(item)

        # Copy fields from game item to Pydantic model
        if hasattr(self._factory.PB_CLASS, "model_fields"):
            # Pydantic model
            for field in self._factory.PB_CLASS.model_fields.keys():
                if hasattr(new_item, field):
                    setattr(pb, field, getattr(new_item, field))

        new_item._pb = pb
        self._items.append(new_item)
        return new_item


class ResourceAmounts(BaseModel):
    clay: int = 0
    ore: int = 0
    energy: int = 0

    def get(self, resource: str, default: int = 0) -> int:
        return getattr(self, resource, default)

    def __iter__(self):
        yield ("clay", self.clay)
        yield ("ore", self.ore)
        yield ("energy", self.energy)


class Prerequisites(ResourceAmounts):
    items: List[str] = Field(default_factory=list)
    research: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)

    @root_validator(pre=True)
    def wrap_in_list(cls, values):
        for field in ["items", "research", "triggers"]:
            if field in values and not isinstance(values[field], (list, tuple)):
                values[field] = [values[field]]
        return values


class Effects(ResourceAmounts):
    enable_commands: List[str] = Field(default_factory=list)
    enable_items: List[str] = Field(default_factory=list)
    enable_resources: List[str] = Field(default_factory=list)
    enable_research: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)

    # Resources to be granted
    clay: int = 0
    ore: int = 0
    energy: int = 0

    @root_validator(pre=True)
    def wrap_in_list(cls, values):
        for field in [
            "enable_commands",
            "enable_items",
            "enable_resources",
            "enable_research",
            "events",
            "triggers",
        ]:
            if field in values and not isinstance(values[field], (list, tuple)):
                values[field] = [values[field]]
        return values


class BaseItem(BaseModel):
    """Pydantic base class for game items."""

    name: str
    difficulty: float = 0
    description: str = ""
    prerequisites: Prerequisites = Field(default_factory=Prerequisites)
    effects: Effects = Field(default_factory=Effects)
    cost: ResourceAmounts = Field(default_factory=ResourceAmounts)
    strings: Dict[str, str] = Field(default_factory=dict)

    # Use model_config to allow arbitrary types
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str = "", **data):
        """Initialise an item."""
        if name:
            data["name"] = name
        super().__init__(**data)
        # Set _pb as a private attribute after initialization
        self._pb = None

    @classmethod
    def from_dict(cls, name, data):
        """Load an item from dict representation."""
        # Process prerequisites
        data["name"] = name
        return cls.model_validate(data)

    def __repr__(self):
        """String representation of the item."""
        return str(self.name)

    def __str__(self):
        """String representation of the item."""
        return str(self.name)

    def __setattr__(self, key, value):
        """Override attribute setter to sync with attached storage model (_pb)."""
        # Let Pydantic handle its own fields first
        super().__setattr__(key, value)

        # Also sync to _pb if it exists and the key is a serializable field
        if hasattr(self, "_pb") and self._pb is not None and key != "_pb":
            # Check if it's a protobuf object
            if hasattr(self._pb.__class__, "DESCRIPTOR"):
                if key in self._pb.__class__.DESCRIPTOR.fields_by_name.keys():
                    setattr(self._pb, key, value)
            # Check if it's a Pydantic model
            elif hasattr(self._pb, "model_fields"):
                if key in self._pb.model_fields:
                    setattr(self._pb, key, value)

    def __getattribute__(self, key):
        """Override attribute getter with fallback to storage model (_pb) if needed."""
        try:
            # Try to get from the Pydantic model first
            return super().__getattribute__(key)
        except AttributeError:
            # If attribute doesn't exist on the Pydantic model, try _pb
            if hasattr(self, "_pb") and self._pb and key != "_pb":
                # Check if it's a protobuf object
                if hasattr(self._pb.__class__, "DESCRIPTOR"):
                    if key in self._pb.__class__.DESCRIPTOR.fields_by_name.keys():
                        return getattr(self._pb, key)
                # Check if it's a Pydantic model
                elif hasattr(self._pb, "model_fields"):
                    if key in self._pb.model_fields:
                        return getattr(self._pb, key)
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )


class BaseFactory:
    """Factory pattern to instantiate items."""

    FIXTURES = "collection.toml"
    ITEM_CLASS = BaseItem
    PB_CLASS = None

    def __init__(self, game):
        """Initialise the Factory.

        Args:
            game (shellcraft.shellcraft.Game): Game object.
        """
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", self.FIXTURES
        )
        data = toml.load(path)
        self.all_items = {
            name: self.ITEM_CLASS.from_dict(name, data) for name, data in data.items()
        }
        self.game = game

    def get(self, item_name) -> BaseItem:
        """Get an item instance by name."""
        if isinstance(item_name, BaseItem):
            return item_name
        item = self.all_items.get(item_name)
        if not item:
            raise ValueError(f"Item {item_name} not found")
        return item

    def make(self, source) -> BaseItem:
        """Create a new unique item from a source.

        The source may be a string, in which case the item is created from
        the item library defined in a TOML file, or it may be a Protobuf message,
        which is typically the case when loading a saved game and instantiating
        serialized items (such as tools or missions), or it may be another Item
        instance which will be copied.
        """
        if isinstance(source, str):
            return copy(self.get(source))
        elif self.PB_CLASS and isinstance(source, self.PB_CLASS):
            item = copy(self.get(source.name))
            return item
        else:
            return copy(source)

    @property
    def available_items(self):
        """Return all items that are currently available."""
        return [item for item in self.all_items.values() if self.is_available(item)]

    def _resources_missing_to_craft(self, item_name):
        item = self.get(item_name)

        return {
            res: int(res_cost - self.game.resources.get(res))
            for res, res_cost in item.cost
            if res_cost - self.game.resources.get(res) > 0
        }

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
        for command in item.effects.enable_commands:
            if command not in self.game.state.commands_enabled:
                self.game.alert("You unlocked the `{}` command", command)
                self.game.state.commands_enabled.append(command)

        # Enable resouces
        for resources in item.effects.enable_resources:
            if resources not in self.game.state.resources_enabled:
                self.game.alert("You can now mine *{}*.", resources)
                self.game.state.resources_enabled.append(resources)

        # Enable items
        for item_name in item.effects.enable_items:
            if item_name not in self.game.state.tools_enabled:
                self.game.alert("You can now craft ${}$.", item_name)
                self.game.state.tools_enabled.append(item_name)

        # Enable research
        for research in item.effects.enable_research:
            if research not in self.game.state.research_enabled:
                self.game.alert("You can now research @{}@.", research)
                self.game.state.research_enabled.append(research)

        # Trigger flags
        for trigger in item.effects.triggers:
            if trigger not in self.game.state.triggers:
                self.game.state.triggers.append(trigger)

        # Grant resources
        for resource in RESOURCES:
            if resource in item.effects:
                value = to_float(item.effects[resource])
                self.game.resources.add(resource, value)
                if value > 0:
                    self.game.alert("You found *{} {}*.", value, resource)
                else:
                    self.game.alert("You lost *{} {}*.", -value, resource)

        # Change mining difficulty
        for resource in RESOURCES:
            change = getattr(item.effects, f"{resource}_mining_difficulty", None)
            if change:
                change = to_float(change)
                self.game.mining_difficulty.multiply(resource, 1 - change)
                self.game.alert(
                    "*{}* mining difficulty reduced by {:.0%}.", resource, change
                )

        # Trigger events
        self.game.events.trigger(*item.effects.events)

    def is_available(self, item_name):
        """Return true if the prerequisites for an item are met."""
        item = self.get(item_name)
        if not item:
            return False
        for resource in RESOURCES:
            if self.game.resources.get(resource) < item.prerequisites.get(resource, 0):
                return False
        for required_item in item.prerequisites.items:
            if not self.game.has_item(required_item):
                return False
        for research in item.prerequisites.research:
            if research not in self.game.state.research_completed:
                return False
        for trigger in item.prerequisites.triggers:
            if trigger not in self.game.state.triggers:
                return False
        return True
