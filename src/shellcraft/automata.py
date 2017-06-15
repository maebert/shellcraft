# -*- coding: utf-8 -*-
"""Automaton Class."""
from __future__ import absolute_import
from shellcraft.epithets import Library, Epithet
from random import seed, randint, paretovariate, random
import math
import re


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
        if re.search(r"\d", name):
            self.name = Automaton.shortcode_to_name(name)
        else:
            self.name = name.splitlines()[:6]
        self._cells = []
        self._padder = Library.get('S', self, -1, -1)
        for y in range(6):
            row = [Library.get(self.name[y][x], self, x, y) for x in range(12)]
            self._cells.append(row)

        self.direction = 0  # Up
        self.x = 0
        self.y = 0

    @property
    def shortcode(self):
        return Automaton.name_to_shortcode(self.name)

    @classmethod
    def shortcode_to_name(cls, shortcode):
        """Convert a shortcode to a name.

        Example:
            Automaton.shortcode_to_name("30LA3M26")
            ['            ', '            ', '      LA   M', ...]
        """
        name = re.sub(r'\d+', lambda m: " " * int(m.group(0)), shortcode)
        return [name[n:n + 12] for n in range(0, 72, 12)]

    @classmethod
    def name_to_shortcode(cls, name):
        """Convert a name to a shortcode.

        Example:
            Automaton.shortcode_to_name(['            ', '            ', '   LA   M   '])
            "27LA3M3"
        """
        shortcode = re.sub(r"[{}]+".format(Epithet.BLANKS), lambda m: str(len(m.group(0))), "".join(name))
        return shortcode.replace('\n', "")

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

    @property
    def epithets(self):
        """Yield all epithets in the body."""
        for row in self._cells:
            for epithet in row:
                yield epithet

    @property
    def weak_epithets(self):
        """Yield all weakly active epithets."""
        return filter(lambda epithet: epithet.state == 1, self.epithets)

    @property
    def active_epithets(self):
        """Yield all active epithets."""
        return filter(lambda epithet: epithet.state == 2, self.epithets)

    @property
    def special_epithets(self):
        """Yield all epithets with non-empty symbols."""
        return filter(lambda epithet: epithet.is_special, self.epithets)

    def step(self):
        # Weak epithets die
        for epithet in self.weak_epithets:
            epithet._next_state = 0

        # Active epithets transport their energy
        for epithet in self.active_epithets:
            epithet.traverse()

        for epithet in self.special_epithets:
            epithet.apply()

        # Apply the next state
        for epithet in self.epithets:
            epithet.update()

        # Padders always day
        self._padder.state = 0
