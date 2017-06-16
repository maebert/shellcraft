# -*- coding: utf-8 -*-
"""Epithet Classes."""

import re


class Name(object):
    def __init__(self, name_or_shortcode):
        if re.search(r"\d", name_or_shortcode):
            self.name = Name.shortcode_to_name(name_or_shortcode)
        else:
            self.name = name_or_shortcode.splitlines()[:6]
        self._cells = []
        self._padder = Epithet.get('S', self, -1, -1)
        for y in range(6):
            row = [Epithet.get(self.name[y][x], self, x, y) for x in range(12)]
            self._cells.append(row)

    @property
    def shortcode(self):
        return Name.name_to_shortcode(self.name)

    @classmethod
    def shortcode_to_name(cls, shortcode):
        """Convert a shortcode to a name.

        Example:
            Name.shortcode_to_name("30LA3M26")
            ['            ', '            ', '      LA   M', ...]
        """
        name = re.sub(r'\d+', lambda m: " " * int(m.group(0)), shortcode)
        return [name[n:n + 12] for n in range(0, 72, 12)]

    @classmethod
    def name_to_shortcode(cls, name):
        """Convert a name to a shortcode.

        Example:
            Name.shortcode_to_name(['            ', '            ', '   LA   M   '])
            "27LA3M3"
        """
        shortcode = re.sub(r"[{}]+".format(Epithet.BLANKS), lambda m: str(len(m.group(0))), "".join(name))
        return shortcode.replace('\n', "")

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
        effects = []

        # Weak epithets die
        for epithet in self.weak_epithets:
            epithet._next_state = 0

        # Active epithets transport their energy
        for epithet in self.active_epithets:
            epithet.traverse()

        for epithet in self.special_epithets:
            effects.append(epithet.apply())

        # Apply the next state
        for epithet in self.epithets:
            epithet.update()

        # Padders always day
        self._padder.state = 0
        return filter(bool, effects)


class Epithet(object):
    symbol = " "
    traversing = True
    period = 4
    generative = False

    BLANKS = " *."

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.state = 0
        self._next_state = 0
        self.value = 0
        self._next_value = 0

    @classmethod
    def get(cls, symbol, name, x=None, y=None):
        for epithet in cls.__subclasses__():
            if epithet.symbol == symbol:
                return epithet(name, x, y)
        return cls(name, x, y)

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
            return self.name._cells[self.y - 1][self.x]
        return self.name._padder

    @property
    def below(self):
        """Select the cell below."""
        if self.y < 5:
            return self.name._cells[self.y + 1][self.x]
        return self.name._padder

    @property
    def right(self):
        """Select the cell right."""
        if self.x < 11:
            return self.name._cells[self.y][self.x + 1]
        return self.name._padder

    @property
    def left(self):
        """Select the cell left."""
        if self.x >= 0:
            return self.name._cells[self.y][self.x - 1]
        return self.name._padder

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
            return "move"


class Turn(Epithet):
    """Epithet that when activated will turn the automaton right."""

    symbol = "D"
    traversing = True

    def apply(self):
        if self.state == 2:
            return "turn_right"


class LeftTurn(Epithet):
    """Epithet that when activated will turn the automaton right."""

    symbol = "G"
    traversing = True

    def apply(self):
        if self.state == 2:
            return "turn_left"


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
