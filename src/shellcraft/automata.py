# -*- coding: utf-8 -*-
"""Automaton Class."""
from __future__ import absolute_import
from shellcraft.epithets import Name
from random import seed, randint, paretovariate, random
import math


class World(object):
    def __init__(self, game, width, height):
        self.game = game
        self.width, self.height = width, height
        self.cache = {}

        # Distribute resources
        hills = width * height // 50
        clay_deposits = width * height // 150
        ore_deposits = width * height // 250

        self.deposits = {
            'ore': [(randint(0, width), randint(0, height), random() * math.pi / 2) for _ in range(clay_deposits)],
            'elevation': [(randint(0, width), randint(0, height), random() * math.pi / 2) for _ in range(hills)],
            'clay': [(randint(0, width), randint(0, height)) for _ in range(ore_deposits)]
        }

    def _resource_pr(self, resource, x, y, distance, deposit):
        seed("{}.{}".format(x, y))
        if resource == 'clay':
            v = paretovariate(2) / (distance + 1)
            return v if v > .2 else 0
        if resource == 'elevation':
            return paretovariate(4) / (distance + 1)
        if resource == 'ore':
            dx, dy, dr = deposit
            angle = math.atan2(dy - y, dx - x) % math.pi
            diff = .5 / (angle - dr + .5)
            v = paretovariate(2) / (distance + 1) * diff
            return v if v > .4 else 0

    def _nearest_deposit(self, resource, x, y):
        bd = 9999999
        best_deposit = None
        for deposit in self.deposits[resource]:
            dx, dy = deposit[:2]
            absx, absy = abs(dx - x), abs(dy - y)
            absx = min(absx, self.width - absx)
            absy = min(absy, self.height - absy)
            d = math.sqrt(absx ** 3 + absy ** 3)
            if d < bd:
                bd = d
                best_deposit = deposit
        return bd, best_deposit

    def _get_resource(self, resource, x, y):
        """Returns the amount of clay at a certain location."""
        x, y = x % self.width, y % self.height
        if (x, y, resource) in self.cache:
            return self.cache[(x, y, resource)]

        distance, deposit = self._nearest_deposit(resource, x, y)
        self.cache[(x, y, resource)] = self._resource_pr(resource, x, y, distance, deposit)
        return self.cache[(x, y, resource)]

    def get_resources(self, x, y):
        x, y = x % self.width, y % self.height
        return {
            'clay': self._get_resource('clay', x, y),
            'ore': self._get_resource('ore', x, y),
            'elevation': self._get_resource('elevation', x, y),
        }


class Automaton(object):
    def __init__(self, name):
        self.name = Name(name)
        self.direction = 0  # Up
        self.x = 0
        self.y = 0

    def move(self):
        """Move one step into the current direction."""
        delta = [(-1, 0), (0, 1), (1, 0), (0, -1)][self.direction]
        self.y += delta[0]
        self.x += delta[1]

    def turn_right(self):
        """Change orientation."""
        self.direction = (self.direction + 1) % 4

    def turn_left(self):
        """Change orientation."""
        self.direction = (self.direction - 1) % 4

    def step(self):
        for effect in self.name.step():
            getattr(self, effect)()
