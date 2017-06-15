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
    traversing = True
    period = 4
    generative = False

    BLANKS = " *."

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
        return self.symbol not in self.BLANKS

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

    def traverse(self, force=False):
        """Apply activity to neighbouring cells."""
        if not self.traversing and not force:
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
    """Epithet that when activated will move the automaton."""

    symbol = "M"
    traversing = True

    def apply(self):
        if self.state == 2:
            self.automaton.move()

class Turn(Epithet):
    """Epithet that when activated will turn the automaton right."""

    symbol = "D"
    traversing = True

    def apply(self):
        if self.state == 2:
            self.automaton.turn_right()

class LeftTurn(Epithet):
    """Epithet that when activated will turn the automaton right."""

    symbol = "G"
    traversing = True

    def apply(self):
        if self.state == 2:
            self.automaton.turn_left()


class Life(Epithet):
    """Epithet that generates a weak charge every 5 cycles."""

    symbol = "L"
    generative = True

    def apply(self):
        self._next_value = (self.value + 1) % self.period
        if self.value == 0:
            # Only weakly activate if not already activated
            self._next_state = max(self._next_state, 1)


class Amplify(Epithet):
    """Epithet that will amplify a weak charge and allow it to travese."""

    symbol = "A"

    def apply(self):
        if self.state != 2:
            for c in self.neighbours:
                if c.generative and c.state == 1:
                    self._next_state = 2
                    c._next_state = max(c._next_state, 1)


class Concurrence(Epithet):
    """Epithet that will split a charge into two horizontal charges."""

    symbol = "C"

    def traverse(self):
        """Apply activity to neighbouring cells."""
        if self.above.state == 1 or self.below.state == 1:
            self.left._next_state = 2
            self.right._next_state = 2
        if self.right.state == 1 or self.left.state == 1:
            self.above._next_state = 2
            self.below._next_state = 2
        # ...and turn weak
        self._next_state = 1


class Restraint(Epithet):
    """Epithet that will only traverse it's charge every second time."""

    symbol = "R"
    traversing = False

    def apply(self):
        self._next_value = self.value
        if self.state == 2:
            self._next_value = (self.value + 1)
            self._next_state = 0
            if self.value == 1:
                self._next_value = 0
                self.traverse(force=True)


class Silence(Epithet):
    """Epithet that will can never be charged."""

    symbol = "S"
    traversing = False


class Synchronicity(Epithet):
    """Similar to concurrence, but will only traverse if charged from both sides."""
    symbol = "Y"

    def traverse(self):
        """Apply activity to neighbouring cells."""
        if self.above.state == 1 and self.below.state == 1:
            self.left._next_state = 2
            self.right._next_state = 2
            self._next_state = 1
        if self.right.state == 1 and self.left.state == 1:
            self.above._next_state = 2
            self.below._next_state = 2
            self._next_state = 1
        else:
            self._next_state = 0
        # ...and turn weak
