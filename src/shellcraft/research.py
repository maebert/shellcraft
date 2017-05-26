# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import BaseItem, BaseFactory


class ResearchProject(BaseItem):
    def __repr__(self):
        return "%{}%".format(self.name)


class ResearchFactory(BaseFactory):
    FIXTURES = 'research.yaml'
    ITEM_CLASS = ResearchProject

    def is_available(self, item_name):
        project = self.get(item_name)
        return project.name not in self.game.state.research_completed and super(ResearchFactory, self).is_available(project)
