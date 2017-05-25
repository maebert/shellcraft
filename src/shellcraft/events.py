# -*- coding: utf-8 -*-

"""Events Interface."""

from __future__ import absolute_import, division, print_function, unicode_literals

from shellcraft.core import BaseItem, BaseFactory


class Event(BaseItem):
    def __repr__(self):
        return self.name


class EventFactory(BaseFactory):
    FIXTURES = 'events.yaml'
    ITEM_CLASS = Event

    def trigger(self, *events):
        for event in events:
            event = self.get(event)
            self.game.alert(event.description)
            self.apply_effects(event)
