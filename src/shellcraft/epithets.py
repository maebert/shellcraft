# -*- coding: utf-8 -*-
"""Epithet Classes."""
from __future__ import absolute_import
from future.utils import with_metaclass


class Library(type):
    _all = {}

    def __new__(cls, name, bases, attrs):
        epithet = super(Library, cls).__new__(cls, name, bases, attrs)
        cls._all[epithet.symbol] = epithet
        return epithet

    @classmethod
    def get(cls, symbol, automaton, x=None, y=None):
        if symbol not in cls._all:
            symbol = " "
        epithet = cls._all[symbol]
        return epithet(automaton, x, y)


class Epithet(with_metaclass(Library)):
    __metaclass__ = Library
    symbol = " "
    transduces = True

    def __init__(self, automaton, x, y):
        self.automaton = automaton
        self.x = x
        self.y = y
        self.state = 0
        self._next_state = 0
        self.value = 0
        self._next_value = 0

    @property
    def is_special(self):
        return self.symbol not in " *"

    @property
    def neighbours(self):
        """Generate all the neighbours."""
        yield self.above
        yield self.below
        yield self.left
        yield self.right

    @property
    def above(self):
        """Select the cell above."""
        if self.y >= 0:
            return self.automaton._cells[self.y - 1][self.x]
        return self.automaton._padder

    @property
    def below(self):
        """Select the cell below."""
        if self.y < 5:
            return self.automaton._cells[self.y + 1][self.x]
        return self.automaton._padder

    @property
    def right(self):
        """Select the cell right."""
        if self.x < 11:
            return self.automaton._cells[self.y][self.x + 1]
        return self.automaton._padder

    @property
    def left(self):
        """Select the cell left."""
        if self.x >= 0:
            return self.automaton._cells[self.y][self.x - 1]
        return self.automaton._padder

    def apply(self):
        pass

    def transduce(self):
        """Apply activity to neighbouring cells."""
        if not self.transduces:
            return
        if self.above.state == 1:
            self.below._next_state = 2
        if self.below.state == 1:
            self.above._next_state = 2
        if self.right.state == 1:
            self.left._next_state = 2
        if self.left.state == 1:
            self.right._next_state = 2
        # ...and turn weak
        self._next_state = 1

    def update(self):
        """Update the inner state."""
        self.state = self._next_state
        self._next_state = 0
        self.value = self._next_value
        self._next_value = 0


class Move(Epithet):
    symbol = "M"
    transduces = False

    def apply(self):
        if self.state == 2:
            self.automaton.move()
            self._next_state = 0


class Life(Epithet):
    symbol = "L"

    def apply(self):
        self._next_value = self.value + 1
        if self.value == 4:
            # Only weakly activate if not already activated
            self._next_state = max(self._next_state, 1)
            self._next_value = 0


class Amplify(Epithet):
    symbol = "A"

    def apply(self):
        if self.state != 2:
            for c in self.neighbours:
                if c.is_special and c.state == 1:
                    self._next_state = 2
                    c._next_state = max(c._next_state, 1)


class Split(Epithet):
    symbol = "T"

    def transduce(self):
        """Apply activity to neighbouring cells."""
        if self.above.state == 1 or self.below.state == 1:
            self.left._next_state = 2
            self.right._next_state = 2
        if self.right.state == 1 or self.left.state == 1:
            self.above._next_state = 2
            self.below._next_state = 2
        # ...and turn weak
        self._next_state = 1
