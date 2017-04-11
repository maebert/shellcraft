# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import AbstractItem, AbstractCollection


class ResearchProject(AbstractItem):
    def __repr__(self):
        return "@{}@".format(self.name)


class Research(AbstractCollection):
    FIXTURES = 'research.yaml'
    ITEM_CLASS = ResearchProject

    def is_available(self, item_name):
        project = self.get(item_name)
        return project.name not in self.game.flags.research_completed and super(Research, self).is_available(project)
