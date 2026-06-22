"""Tutorial step catalog and dispatch."""

import re
from typing import ClassVar

from shellcraft._cli_impl import echo, echo_alerts
from shellcraft.core import BaseFactory, BaseItem


class Step(BaseItem):
    FIXTURES: ClassVar[str] = "tutorials.toml"

    def __repr__(self):
        return f"<Tutorial {self.name}>"

    def format_description(self):
        return re.sub(r"(?<!\n)\n(?!\n)", " ", self.description)


class TutorialFactory(BaseFactory):
    ITEM_CLASS = Step

    def get_next_step(self):
        step = self.all_items.get(str(self.game.state.tutorial_step))
        if step is None or not self.is_available(step):
            return None
        return step

    def print_last_step(self):
        step = self.all_items.get(str(self.game.state.tutorial_step - 1))
        if step:
            echo(step.format_description())

    def cont(self):
        step = self.get_next_step()
        if step is None:
            return False
        self.game.state.tutorial_step += 1
        self.apply_effects(step)
        self.game.save()
        echo(step.format_description())
        if self.game._messages:
            echo("")
        echo_alerts(self.game)
        return True


Step._load_catalog()
