# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
import os
import toml


class FractionProxy(object):
    FIXTURES = "fractions.toml"

    def __init__(self, field):
        self._field = field
        self._fractions = {f.name: f for f in field}

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", self.FIXTURES
        )
        data = toml.load(path)
        for name, fraction in data.items():
            if name not in self._fractions:
                from shellcraft.game_state import Fraction
                f = Fraction(name=name, influence=fraction["influence"])
                self._field.append(f)
                self._fractions[name] = f

    def get(self, name):
        return self._fractions[name]

    def __getattr__(self, name):
        if name in self._fractions:
            return self._fractions[name]
        raise AttributeError
