# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
import os
import yaml


class FractionProxy(object):
    FIXTURES = 'fractions.yaml'

    def __init__(self, field):
        self._field = field
        self._fractions = {f.name: f for f in field}

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", self.FIXTURES)) as f:
            for name, fraction in yaml.load(f).items():
                if name not in self._fractions:
                    f = self._field.add(name=name, influence=fraction['influence'])
                    self._fractions[name] = f

    def get(self, name):
        return self._fractions[name]

    def __getattr__(self, name):
        if name in self._fractions:
            return self._fractions[name]
        raise AttributeError
