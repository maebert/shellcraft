"""Pydantic models for persisted ShellCraft game state.

Everything in this module is data: model classes carry the state that gets
serialized to disk. Runtime behavior (mining, crafting, mission completion)
lives in `shellcraft.shellcraft.Game` and the factories under `shellcraft.*`.

Catalog data (tool durability, mission text templates, etc.) is *not* stored
here — saved instances reference catalog entries by `name` and look them up
lazily via the `.catalog` / `.template` properties.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Action(BaseModel):
    """An in-progress mine/craft/research action."""

    task: str = ""
    target: str = ""
    completion: Optional[datetime] = None


class Fraction(BaseModel):
    """A faction the player can build reputation with."""

    name: str = ""
    influence: float = 0.0
    missions_completed: int = 0
    missions_failed: int = 0


class Resources(BaseModel):
    """Container for the three resource types with arithmetic helpers.

    Used for the player's pool, mining difficulty, mining-difficulty increment,
    and lifetime totals.
    """

    clay: float = 0.0
    ore: float = 0.0
    energy: float = 0.0

    def get(self, resource: str, default: float = 0.0) -> float:
        return getattr(self, resource, default)

    def add(self, resource: str, value: float) -> None:
        setattr(self, resource, getattr(self, resource, 0) + value)

    def multiply(self, resource: str, factor: float) -> None:
        setattr(self, resource, getattr(self, resource, 0) * factor)

    def __iter__(self):
        yield ("clay", self.clay)
        yield ("ore", self.ore)
        yield ("energy", self.energy)


class ToolInstance(BaseModel):
    """A tool the player owns. Static stats live on the catalog entry."""

    name: str
    condition: float = 0

    @property
    def catalog(self):
        from shellcraft.tools import Tool

        return Tool.get(self.name)

    def __str__(self):
        return self.catalog.describe_wear(self.condition)

    def __repr__(self):
        return f"<ToolInstance {self.name} {self.condition}>"


class NPC(BaseModel):
    first: str = ""
    middle: str = ""
    last: str = ""
    title: str = ""
    nickname: str = ""
    display: str = ""
    fraction_name: str = ""


class MissionInstance(BaseModel):
    """A mission the player has accepted. Text templates live on the catalog."""

    name: str
    demand: int = 0
    reward: int = 0
    demand_type: str = ""
    reward_type: str = ""
    due: int = 0
    deadline: Optional[datetime] = None
    writer: Optional[NPC] = None
    reward_factor: int = 0

    @property
    def template(self):
        from shellcraft.missions import Mission

        return Mission.get(self.name)


class Stats(BaseModel):
    total_game_duration: float = 0.0
    total_mined: Resources = Field(default_factory=Resources)


class GameState(BaseModel):
    """Root of the persisted save file."""

    debug: bool = False

    action: Optional[Action] = None
    tools: List[ToolInstance] = Field(default_factory=list)
    missions: List[MissionInstance] = Field(default_factory=list)
    resources: Resources = Field(default_factory=Resources)

    tools_enabled: List[str] = Field(default_factory=list)
    resources_enabled: List[str] = Field(default_factory=list)
    commands_enabled: List[str] = Field(default_factory=list)
    research_enabled: List[str] = Field(default_factory=list)
    research_completed: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)

    mining_difficulty: Resources = Field(default_factory=Resources)
    mining_difficulty_increment: Resources = Field(default_factory=Resources)

    trade_reputation: float = 0.0
    tutorial_step: int = 0

    stats: Stats = Field(default_factory=Stats)
    fractions: List[Fraction] = Field(default_factory=list)
