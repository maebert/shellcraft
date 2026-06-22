"""Game state machine: mining, crafting, research, missions."""

import datetime
import os
from random import random
from typing import Any

import shellcraft.fractions as fractions
from shellcraft.core import BaseItem
from shellcraft.events import EventFactory
from shellcraft.exceptions import BusyException
from shellcraft.game_state import (
    Action,
    Fraction,
    GameState,
    MissionInstance,
    Resources,
    ToolInstance,
)
from shellcraft.missions import MissionFactory
from shellcraft.research import ResearchFactory
from shellcraft.tools import ToolFactory
from shellcraft.tutorial import TutorialFactory


class Game:
    """Owns the persisted state and the catalogs/factories that operate on it."""

    def __init__(self, state: GameState | None = None) -> None:
        self.state = state or GameState()
        self._messages: list[str] = []

        self.lab = ResearchFactory(self)
        self.workshop = ToolFactory(self)
        self.tutorial = TutorialFactory(self)
        self.events = EventFactory(self)
        self.mission_factory = MissionFactory(self)

        self.save_file: str | None = None

    # ---------- direct state accessors ----------

    @property
    def resources(self) -> Resources:
        return self.state.resources

    @property
    def mining_difficulty(self) -> Resources:
        return self.state.mining_difficulty

    @property
    def mining_difficulty_increment(self) -> Resources:
        return self.state.mining_difficulty_increment

    @property
    def total_mined(self) -> Resources:
        return self.state.stats.total_mined

    @property
    def missions(self) -> list[MissionInstance]:
        return self.state.missions

    @property
    def tools(self) -> list[ToolInstance]:
        """Owned items with catalog type == 'tool' (excludes automata)."""
        return [t for t in self.state.tools if t.catalog.type == "tool"]

    @property
    def automata(self) -> list[ToolInstance]:
        return [t for t in self.state.tools if t.catalog.type == "automaton"]

    @property
    def fractions(self) -> dict[str, Fraction]:
        """Faction state keyed by name."""
        return {f.name: f for f in self.state.fractions}

    # ---------- messaging ----------

    def alert(self, msg: str, *args: Any) -> None:
        self._messages.append(msg.format(*args))

    @property
    def is_busy(self) -> bool:
        if self.state.action and self.state.action.task:
            completion = self.state.action.completion
            if completion is None:
                return False
            now = datetime.datetime.now()
            if completion.tzinfo is not None:
                completion = completion.replace(tzinfo=None)
            if now.tzinfo is not None:
                now = now.replace(tzinfo=None)
            if now > completion:
                self.state.action = None
                return False
            return True
        return False

    # ---------- missions ----------

    def add_mission(self, name: str) -> MissionInstance | None:
        return self.mission_factory.add(name)

    def complete_missions(self) -> None:
        self.mission_factory.complete_due()

    # ---------- core actions ----------

    def craft(self, tool_name: "str | BaseItem") -> float:
        item = self.workshop.get(tool_name)
        for resource, res_cost in item.cost:
            if res_cost:
                self.resources.add(resource, -res_cost)
        instance = ToolInstance(name=item.name, condition=max(item.durability, 0))
        self.state.tools.append(instance)
        self._act("craft", item.name, item.difficulty)
        self.alert("Crafted {}", item)
        return item.difficulty

    def research(self, project_name: "str | BaseItem") -> float:
        project = self.lab.get(project_name)
        self.state.research_completed.append(project.name)
        self._act("research", project.name, project.difficulty)
        self.alert("Researched {}.", project)
        self.lab.apply_effects(project)
        return project.difficulty

    def has_item(self, item_name: str) -> bool:
        return any(t.name == item_name for t in self.state.tools)

    def _best_mining_tool(self, resource: str) -> ToolInstance | None:
        candidates = [t for t in self.state.tools if t.catalog.type == "tool"]
        if not candidates:
            return None
        return max(candidates, key=lambda t: t.catalog.mining_bonus.get(resource, 0))

    def mine(self, resource: str) -> tuple[float, int]:
        if self.is_busy:
            raise BusyException(self)

        difficulty = self.mining_difficulty.get(resource)
        total_wear = 0
        efficiency = 0
        events = []

        while total_wear < difficulty:
            tool = self._best_mining_tool(resource)
            if tool is None:
                break

            bonus = tool.catalog.mining_bonus.get(resource, 1)
            if tool.condition <= (difficulty - total_wear):
                contribution = tool.condition / difficulty
                total_wear += tool.condition
                efficiency += tool.condition * bonus / difficulty
                self.alert(f"Destroyed ${tool.name}$ while mining *{resource}*.")
                self.state.tools.remove(tool)
            else:
                contribution = (difficulty - total_wear) / difficulty
                tool.condition -= difficulty - total_wear
                total_wear = difficulty

            efficiency += contribution * bonus

            for event, prob in tool.catalog.event_bonus.items():
                if random() * contribution < prob:
                    events.append(event)

        # Hand mining covers any remaining work at base efficiency 1.
        efficiency += (difficulty - total_wear) / difficulty
        efficiency = int(efficiency)

        self.mining_difficulty.add(
            resource, self.mining_difficulty_increment.get(resource)
        )

        self._act("mine", resource, difficulty)
        self.resources.add(resource, efficiency)
        self.total_mined.add(resource, efficiency)

        self._unlock_items()
        self.alert(f"Mined *{efficiency} {resource}*.")
        self.events.trigger(*events)
        return difficulty, efficiency

    def _unlock_items(self) -> None:
        for item in self.workshop.available_items:
            if item.name not in self.state.tools_enabled:
                self.alert("You can now craft {}.", item)
                self.state.tools_enabled.append(item.name)
        for research in self.lab.available_items:
            if research.name not in self.state.research_enabled:
                self.alert("You can now research %{}%.", research.name)
                self.state.research_enabled.append(research.name)

    def _act(self, task: str, target: Any, duration: float) -> None:
        if self.is_busy:
            raise BusyException(self)

        self.state.stats.total_game_duration += duration
        if self.state.debug:
            duration = 0

        self.state.action = Action(
            task=task,
            target=str(target),
            completion=datetime.datetime.now() + datetime.timedelta(seconds=duration),
        )

    # ---------- persistence ----------

    @classmethod
    def load(cls, filename: str) -> "Game":
        with open(filename) as f:
            state = GameState.model_validate_json(f.read())
        game = cls(state)
        game.save_file = filename
        return game

    @classmethod
    def create(cls, filename: str) -> "Game":
        game = cls()
        game.state.mining_difficulty.clay = 0.5
        game.state.mining_difficulty.ore = 0.5
        game.state.mining_difficulty.energy = 0.5
        game.state.mining_difficulty_increment.clay = 0.5
        game.state.mining_difficulty_increment.ore = 0.5
        game.state.mining_difficulty_increment.energy = 0.5
        fractions.seed_defaults(game.state.fractions)

        game.save_file = filename
        save_dir, _ = os.path.split(filename)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
        game.save()
        return game

    def save(self, filename: str | None = None) -> None:
        target = filename or self.save_file
        if target is None:
            raise ValueError("No save_file set; pass a filename explicitly.")
        with open(target, "w") as f:
            f.write(self.state.model_dump_json(indent=2))
