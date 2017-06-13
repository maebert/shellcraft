# -*- coding: utf-8 -*-

"""Events Interface."""

from __future__ import absolute_import, division, print_function, unicode_literals

from shellcraft.core import BaseItem, BaseFactory
from shellcraft._cli_impl import echo, ask
from shellcraft.utils import convert_resource_value, format_name
from shellcraft.game_state_pb2 import Mission as MissionPB
from shellcraft.world import NPCFactory
import datetime
import random


class Mission(BaseItem):
    """A trade contract, requesting a certain quantity of a resource in a given time."""

    def randomize(self, game):
        """Generate random mission."""
        self.writer = NPCFactory.make()
        # print("WRITER IS", self.demand)
        # self.demand = 23
        # self.writer.fraction = random.choice(game.fractions._fractions)

        random.shuffle(game.state.resources_enabled)
        demand_type, reward_type = game.state.resources_enabled[:2]

        if game.workshop.available_items:
            best_available_tool = max(game.workshop.available_items, key=lambda item: item.mining_bonus.get(demand_type, 0))
            efficiency = best_available_tool.mining_bonus.get(demand_type) or 1
        else:
            efficiency = 1

        difficulty = game.mining_difficulty.get(demand_type)

        extra_demand = random.random() * game.resources.get(demand_type)

        self.demand = int(game.resources.get(demand_type) + extra_demand)
        self.due = int(extra_demand / efficiency * difficulty * (2 + random.random())) + 10
        self.demand_type = demand_type
        self.reward = int((1 + game.state.trade_reputation + .3 * random.random()) * convert_resource_value(demand_type, reward_type) * self.demand)
        self.reward_type = reward_type
        # a = str(self.writer)
        # print("DEM", format_name(self.writer))
        # self.writer.CopyFrom(npc)

    def vars(self, game):
        return {
            "writer": format_name(self.writer),
            "demand": self.demand,
            "due": self.due,
            "demand_type": self.demand_type,
            "reward": self.reward,
            "reward_type": self.reward_type,
            "deficit": self.demand - game.resources.get(self.demand_type)
        }

    def offer(self, game):
        # return re.sub("  +", " ", d.replace("\n", " "))
        echo(self.strings['intro'].format(**self.vars(game)))
        if ask(self.strings['ask'].format(**self.vars(game))):
            self.deadline.FromDatetime(datetime.datetime.now() + datetime.timedelta(seconds=self.due))
            echo(self.strings['agree'].format(**self.vars(game)))
            return True
        else:
            game.state.trade_reputation -= 0.02
            echo(self.strings['disagree'].format(**self.vars(game)))
            return False

    def is_completed(self, game):
        if datetime.datetime.now() > self.deadline.ToDatetime():
            # Failed!
            echo(self.strings['failed'].format(**self.vars(game)))
            return True
        if game.resources.get(self.demand_type) >= self.demand:
            echo(self.strings['completed'].format(**self.vars(game)))
            game.resources.add(self.demand_type, -self.demand)
            game.resources.add(self.reward_type, self.reward)
            return True
        return False

    def __repr__(self):
        return "blank"
        return "<{demand} {demand_type} in {due}s for {reward} {reward_type}>".format(**vars(self))


class MissionFactory(BaseFactory):
    FIXTURES = 'missions.yaml'
    ITEM_CLASS = Mission
    PB_CLASS = MissionPB

    def make(self, mission):
        new_mission = super(MissionFactory, self).make(mission)
        if not hasattr(new_mission, "demand"):
            new_mission.randomize(self.game)
        return new_mission
