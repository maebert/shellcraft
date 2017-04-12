# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import AbstractItem, AbstractCollection, convert_resource_value
from shellcraft._cli_impl import echo, ask
import random
import re


class Contract(object):
    """A trade contract, requesting a certain quantity of a resource in a given time."""

    def __init__(self, game):
        self.game = game

        random.shuffle(game.flags.resources_enabled)
        self.demand, self.reward = game.flags.resources_enabled[:2]
        if game.tools.available_items:
            best_available_tool = max(game.tools.available_items, key=lambda item: item.mining_bonus.get(self.demand, 0))
            efficiency = best_available_tool.mining_bonus.get(self.demand)
        else:
            efficiency = 1

        difficulty = game.flags.mining_difficulty.get(self.demand)

        demand = random.random() * game.resources.get(self.demand)

        self.due = int(demand / efficiency * difficulty * (1 + random.random()))
        self.demand_q = int(game.resources.get(self.demand) + demand)

        self.reward_q = int((game.flags.trade_reputation + .3 * random.random()) * convert_resource_value(self.demand, self.reward) * self.demand_q)

    @property
    def description(self):
        d = """A trader asks whether you can supply them with *{demand_q} {demand}* in
        {due} seconds or less. In return, they offer *{reward_q} {reward}*. You need
        mine another *{deficit} {demand}* to meet the deadline.""".format(deficit=self.demand_q - self.game.resources.get(self.demand), **vars(self))
        return re.sub("  +", " ", d.replace("\n", " "))

    def offer(self):
        echo(self.description)
        if ask("Do you agree to this trade contract?"):
            echo("The *{}* will be automatically collected as soon as you have enough. Time is of the essence now!", self.demand)
        else:
            self.game.flags.trade_reputation -= 0.02
            echo("The trader leaves, disappointed.")

    def to_dict(self):
        return {
            "demand_q": self.demand_q,
            "demand": self.demand,
            "due": self.due,
            "reward_q": self.reward_q,
            "reward": self.reward
        }

    def __repr__(self):
        return "<{demand_q} {demand} in {due}s for {reward_q} {reward}>".format(**vars(self))


class Event(AbstractItem):
    def __repr__(self):
        return self.name


class Events(AbstractCollection):
    FIXTURES = 'events.yaml'
    ITEM_CLASS = Event

    def trigger(self, *events):
        for event in events:
            event = self.get(event)
            self.game.alert(event.description)
            self.apply_effects(event)
