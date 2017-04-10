# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import AbstractItem, AbstractCollection


class ResearchProject(AbstractItem):
    def __repr__(self):
        return "@{}@".format(self.name)

    @classmethod
    def from_dict(cls, name, data):
        project = super().from_dict(name, data)
        project.difficulty = data.get("difficulty", -1)
        return project


class Research(AbstractCollection):
    FIXTURES = 'research.yaml'
    ITEM_CLASS = ResearchProject
