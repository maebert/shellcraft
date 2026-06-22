"""Mission catalog (text templates) and runtime mission helpers."""

import datetime
import random
from typing import ClassVar

from shellcraft._cli_impl import ask, echo
from shellcraft.core import BaseFactory, BaseItem
from shellcraft.game_state import MissionInstance
from shellcraft.utils import convert_resource_value, format_name
from shellcraft.world import NPCFactory


class Mission(BaseItem):
    """Text template for a mission/contract. Runtime state lives on MissionInstance."""

    reward_type: str = ""

    FIXTURES: ClassVar[str] = "missions.toml"


class MissionFactory(BaseFactory):
    ITEM_CLASS = Mission

    def add(self, name: str):
        """Construct, randomize, and offer a new mission.

        If the player accepts, the instance is appended to game state and returned.
        Otherwise returns None.
        """
        instance = MissionInstance(name=name)
        # Carry default reward_type from the template, if any.
        template = self.get(name)
        if template.reward_type and not instance.reward_type:
            instance.reward_type = template.reward_type
        self._randomize(instance)
        if self._offer(instance):
            self.game.state.missions.append(instance)
            return instance
        return None

    def complete_due(self) -> None:
        """Remove any missions that resolved (succeeded or failed)."""
        for mission in list(self.game.state.missions):
            if self._is_completed(mission):
                self.game.state.missions.remove(mission)

    def _vars(self, mission: MissionInstance) -> dict:
        return {
            "writer": format_name(mission.writer),
            "demand": mission.demand,
            "due": mission.due,
            "demand_type": mission.demand_type,
            "reward": mission.reward,
            "reward_type": mission.reward_type,
            "deficit": mission.demand - self.game.resources.get(mission.demand_type),
        }

    def _randomize(self, mission: MissionInstance) -> None:
        game = self.game
        mission.writer = NPCFactory.make()
        random.shuffle(game.state.resources_enabled)

        if not mission.reward_type or mission.reward_type == "resource":
            demand_type, reward_type = game.state.resources_enabled[:2]
        elif mission.reward_type == "reputation":
            demand_type = game.state.resources_enabled[1]
            reward_type = mission.reward_type
        else:
            demand_type = game.state.resources_enabled[0]
            reward_type = mission.reward_type

        if game.workshop.available_items:
            best_tool = max(
                game.workshop.available_items,
                key=lambda item: item.mining_bonus.get(demand_type, 0),
            )
            efficiency = best_tool.mining_bonus.get(demand_type) or 1
        else:
            efficiency = 1

        difficulty = game.mining_difficulty.get(demand_type)
        extra_demand = random.random() * game.resources.get(demand_type)

        mission.demand = int(game.resources.get(demand_type) + extra_demand)
        mission.due = (
            int(extra_demand / efficiency * difficulty * (2 + random.random())) + 10
        )
        mission.demand_type = demand_type
        mission.reward = int(
            (1 + game.state.trade_reputation + 0.3 * random.random())
            * convert_resource_value(demand_type, reward_type)
            * mission.demand
        )
        mission.reward_type = reward_type

    def _offer(self, mission: MissionInstance) -> bool:
        template = mission.template
        echo(template.strings["intro"].format(**self._vars(mission)))
        if ask(template.strings["ask"].format(**self._vars(mission))):
            mission.deadline = datetime.datetime.now() + datetime.timedelta(
                seconds=mission.due
            )
            echo(template.strings["agree"].format(**self._vars(mission)))
            return True
        self.game.state.trade_reputation -= 0.02
        echo(template.strings["disagree"].format(**self._vars(mission)))
        return False

    def _is_completed(self, mission: MissionInstance) -> bool:
        template = mission.template
        if mission.deadline and datetime.datetime.now() > mission.deadline:
            echo(template.strings["failed"].format(**self._vars(mission)))
            return True
        if self.game.resources.get(mission.demand_type) >= mission.demand:
            echo(template.strings["completed"].format(**self._vars(mission)))
            self.game.resources.add(mission.demand_type, -mission.demand)
            self.game.resources.add(mission.reward_type, mission.reward)
            return True
        return False


Mission._load_catalog()
