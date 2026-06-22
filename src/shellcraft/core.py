"""Catalog base classes and game-bound helpers.

Catalog items (tools, research projects, events, tutorial steps, mission templates)
are pure Pydantic models loaded from TOML at import time into a class-level
`_registry`. Persisted game state lives in `shellcraft.game_state`. Game-bound
helpers (`is_available`, `available_items`, `apply_effects`, etc.) sit on
factories that hold a reference to the active Game.
"""

import os
from typing import Any, ClassVar, Dict, List, Optional, TYPE_CHECKING, TypeVar, cast

import toml
from pydantic import BaseModel, Field, field_validator

from shellcraft.utils import to_float

if TYPE_CHECKING:
    from shellcraft.shellcraft import Game

_T = TypeVar("_T", bound="BaseItem")

RESOURCES = ["clay", "energy", "ore"]


def _wrap_in_list(v: Any) -> list:
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return list(v)
    return [v]


class ResourceAmounts(BaseModel):
    """Integer resource counts. Used for costs and prerequisites."""

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

    @field_validator("items", "research", "triggers", mode="before")
    @classmethod
    def _coerce_list(cls, v: Any) -> list:
        return _wrap_in_list(v)


class Effects(ResourceAmounts):
    enable_commands: List[str] = Field(default_factory=list)
    enable_items: List[str] = Field(default_factory=list)
    enable_resources: List[str] = Field(default_factory=list)
    enable_research: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)

    # Mining-difficulty modifiers carry expressions like "random(.2, .5)";
    # evaluated by `to_float` at apply time.
    clay_mining_difficulty: Optional[str] = None
    ore_mining_difficulty: Optional[str] = None
    energy_mining_difficulty: Optional[str] = None

    @field_validator(
        "enable_commands",
        "enable_items",
        "enable_resources",
        "enable_research",
        "events",
        "triggers",
        mode="before",
    )
    @classmethod
    def _coerce_list(cls, v: Any) -> list:
        return _wrap_in_list(v)


class BaseItem(BaseModel):
    """Base for catalog items. Each subclass owns a class-level `_registry`."""

    name: str
    difficulty: float = 0
    description: str = ""
    prerequisites: Prerequisites = Field(default_factory=Prerequisites)
    effects: Effects = Field(default_factory=Effects)
    cost: ResourceAmounts = Field(default_factory=ResourceAmounts)
    strings: Dict[str, str] = Field(default_factory=dict)

    FIXTURES: ClassVar[str] = ""
    _registry: ClassVar[Optional[Dict[str, "BaseItem"]]] = None

    def __repr__(self) -> str:
        return str(self.name)

    def __str__(self) -> str:
        return str(self.name)

    @classmethod
    def _load_catalog(cls) -> Dict[str, "BaseItem"]:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            cls.FIXTURES,
        )
        data = toml.load(path)
        cls._registry = {
            name: cls.model_validate({**payload, "name": name})
            for name, payload in data.items()
        }
        return cls._registry

    @classmethod
    def all(cls: type[_T]) -> Dict[str, _T]:
        if cls._registry is None:
            return cast(Dict[str, _T], cls._load_catalog())
        return cast(Dict[str, _T], cls._registry)

    @classmethod
    def get(cls: type[_T], name: "str | BaseItem") -> _T:
        if isinstance(name, cls):
            return name
        item = cls.all().get(name)
        if item is None:
            raise ValueError(f"{cls.__name__} '{name}' not found")
        return item


class BaseFactory:
    """Game-bound helpers over a catalog class.

    Concrete subclasses set `ITEM_CLASS` to a `BaseItem` subclass and inherit
    catalog lookup, availability, affordability, and effect application.
    """

    ITEM_CLASS = BaseItem

    def __init__(self, game: "Game") -> None:
        self.game = game

    @property
    def all_items(self) -> Dict[str, BaseItem]:
        return self.ITEM_CLASS.all()

    def get(self, name: "str | BaseItem") -> BaseItem:
        return self.ITEM_CLASS.get(name)

    @property
    def available_items(self) -> List[BaseItem]:
        return [item for item in self.all_items.values() if self.is_available(item)]

    def _resources_missing_to_craft(
        self, item_name: "str | BaseItem"
    ) -> dict[str, int]:
        item = self.get(item_name)
        return {
            res: int(res_cost - self.game.resources.get(res))
            for res, res_cost in item.cost
            if res_cost - self.game.resources.get(res) > 0
        }

    def can_afford(self, item_name: "str | BaseItem") -> bool:
        item = self.get(item_name)
        for resource in RESOURCES:
            if item.cost.get(resource, 0) > self.game.resources.get(resource):
                return False
        return True

    def apply_effects(self, item_name: "str | BaseItem") -> None:
        item = self.get(item_name)
        state = self.game.state

        for command in item.effects.enable_commands:
            if command not in state.commands_enabled:
                self.game.alert("You unlocked the `{}` command", command)
                state.commands_enabled.append(command)

        for resource in item.effects.enable_resources:
            if resource not in state.resources_enabled:
                self.game.alert("You can now mine *{}*.", resource)
                state.resources_enabled.append(resource)

        for tool_name in item.effects.enable_items:
            if tool_name not in state.tools_enabled:
                self.game.alert("You can now craft ${}$.", tool_name)
                state.tools_enabled.append(tool_name)

        for research in item.effects.enable_research:
            if research not in state.research_enabled:
                self.game.alert("You can now research @{}@.", research)
                state.research_enabled.append(research)

        for trigger in item.effects.triggers:
            if trigger not in state.triggers:
                state.triggers.append(trigger)

        for resource in RESOURCES:
            change_expr = getattr(item.effects, f"{resource}_mining_difficulty", None)
            if change_expr:
                change = to_float(change_expr)
                self.game.mining_difficulty.multiply(resource, 1 - change)
                self.game.alert(
                    "*{}* mining difficulty reduced by {:.0%}.", resource, change
                )

        self.game.events.trigger(*item.effects.events)

    def is_available(self, item_name: "str | BaseItem") -> bool:
        item = self.get(item_name)
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
