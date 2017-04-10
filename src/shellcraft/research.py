# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import AbstractItem, AbstractCollection


class ResearchProject(AbstractItem):
    pass



class Research(AbstractCollection):
    FIXTURES = 'research.yaml'
    ITEM_CLASS = ResearchProject
    pass
