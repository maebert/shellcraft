"""Pydantic models for ShellCraft game state."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CompatList(list):
    """A list that provides protobuf-like .add() method for compatibility."""

    def __init__(self, item_class):
        super().__init__()
        self._item_class = item_class

    def add(self, **kwargs):
        """Add a new item with the given kwargs, protobuf-style."""
        item = self._item_class(**kwargs)
        self.append(item)
        return item


class Action(BaseModel):
    """Represents an ongoing action in the game."""

    task: str = ""
    target: str = ""
    completion: Optional[datetime] = None


class Fraction(BaseModel):
    """Represents a faction/fraction in the game."""

    name: str = ""
    influence: float = 0.0
    missions_completed: int = 0
    missions_failed: int = 0


class Resources(BaseModel):
    """Represents the three main resource types in the game."""

    clay: float = 0.0
    ore: float = 0.0
    energy: float = 0.0


class Tool(BaseModel):
    """Represents a tool owned by the player."""

    name: str = ""
    condition: float = 0.0


class NPC(BaseModel):
    """Represents a non-player character."""

    first: str = ""
    middle: str = ""
    last: str = ""
    title: str = ""
    nickname: str = ""
    display: str = ""
    fraction_name: str = ""


class Mission(BaseModel):
    """Represents a mission/contract in the game."""

    name: str = ""
    demand: int = 0
    reward: int = 0
    demand_type: str = ""
    reward_type: str = ""
    due: int = 0
    deadline: Optional[datetime] = None
    writer: Optional[NPC] = None
    reward_factor: int = 0


class Stats(BaseModel):
    """Represents game statistics."""

    total_game_duration: float = 0.0
    total_mined: Resources = Field(default_factory=Resources)


class GameState(BaseModel):
    """Main game state containing all game data."""

    debug: bool = False

    action: Optional[Action] = None
    tools: List[Tool] = Field(default_factory=list)
    missions: List[Mission] = Field(default_factory=list)
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

    def model_post_init(self, __context):
        """Convert regular lists to CompatList for protobuf compatibility."""
        if not isinstance(self.fractions, CompatList):
            compat_fractions = CompatList(Fraction)
            compat_fractions.extend(self.fractions)
            self.fractions = compat_fractions

        if not isinstance(self.tools, CompatList):
            compat_tools = CompatList(Tool)
            compat_tools.extend(self.tools)
            self.tools = compat_tools

        if not isinstance(self.missions, CompatList):
            compat_missions = CompatList(Mission)
            compat_missions.extend(self.missions)
            self.missions = compat_missions
