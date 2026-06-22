"""Event catalog and trigger dispatch."""

from typing import ClassVar

from shellcraft.core import BaseFactory, BaseItem


class Event(BaseItem):
    FIXTURES: ClassVar[str] = "events.toml"


class EventFactory(BaseFactory):
    ITEM_CLASS = Event

    def trigger(self, *event_names: str) -> None:
        for name in event_names:
            event = self.get(name)
            self.game.alert(event.description)
            self.apply_effects(event)


Event._load_catalog()
