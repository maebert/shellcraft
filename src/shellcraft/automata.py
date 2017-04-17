# -*- coding: utf-8 -*-
"""Automaton Class."""
from __future__ import absolute_import
from shellcraft.epithets import Library


class Automaton(object):
    def __init__(self, name):
        self.name = name.splitlines()[:6]
        self._cells = []
        self._padder = Library.get('*', self, -1, -1)
        for y in range(6):
            row = [Library.get(self.name[y][x], self, x, y) for x in range(12)]
            self._cells.append(row)

        self.direction = 0  # Up
        self.x = 0
        self.y = 0

    def move(self):
        """Move one step into the current direction."""
        delta = [(-1, 0), (0, 1), (1, 0), (-1, 0)][self.direction]
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
            epithet.transduce()

        for epithet in self.special_epithets:
            epithet.apply()

        # Apply the next state
        for epithet in self.epithets:
            epithet.update()

        # Padders always day
        self._padder.state = 0
