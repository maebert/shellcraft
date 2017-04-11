# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import AbstractItem, AbstractCollection


class Event(AbstractItem):
    def __repr__(self):
        return self.name


class Events(AbstractCollection):
    FIXTURES = 'events.yaml'
    ITEM_CLASS = Event
