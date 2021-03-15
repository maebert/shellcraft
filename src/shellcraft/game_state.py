from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, global_config
from typing import List, Dict, Any, NewType, Tuple, Optional
from arrow import Arrow, get

global_config.encoders[Arrow] = lambda obj: obj.isoformat()
global_config.decoders[Arrow] = get


@dataclass_json
@dataclass
class Action:
    task: str
    target: str
    completion: Arrow


@dataclass_json
@dataclass
class Fraction:
    name: str
    influence: float
    missions_completed: int
    missions_failed: int


@dataclass_json
@dataclass
class Resources:
    clay: float = 0
    ore: float = 0
    energy: float = 0


@dataclass_json
@dataclass
class Tool:
    name: str
    condition: float


@dataclass_json
@dataclass
class NPC:
    first: str
    middle: str
    last: str
    title: str
    nickname: str
    display: str
    fraction_name: str


@dataclass_json
@dataclass
class Mission:
    name: str
    demand: int
    reward: int
    demand_type: str
    reward_type: str
    due: int
    deadline: Arrow
    writer: NPC
    reward_factor: int


@dataclass_json
@dataclass
class Stats:
    total_game_duration: float = 0
    total_mined: Resources = Resources()


@dataclass_json
@dataclass
class GameState:
    debug: bool = False

    action: Optional[Action] = None
    tools: List[Tool] = field(default_factory=list)
    missions: Optional[Mission] = None
    resources: Resources = Resources()

    tools_enabled: List[str] = field(default_factory=list)
    resources_enabled: List[str] = field(default_factory=list)
    commands_enabled: List[str] = field(default_factory=list)
    research_enabled: List[str] = field(default_factory=list)
    research_completed: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)

    mining_difficulty: Resources = Resources()
    mining_difficulty_increment: Resources = Resources()

    trade_reputation: float = 0
    tutorial_step: int = 0

    stats: Stats = Stats()
    fractions: List[Fraction] = field(default_factory=list)
