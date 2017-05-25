# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import BaseFactory, BaseItem
from shellcraft._cli_impl import echo, echo_tutorial, echo_alerts


class Step(BaseItem):
    def __repr__(self):
        return "<Tutorial {}>".format(self.name)


class TutorialFactory(BaseFactory):
    FIXTURES = "tutorials.yaml"
    ITEM_CLASS = Step

    def get_next_step(self):
        step = self.get(self.game.state.tutorial_step)
        if not step or not self.is_available(step):
            return None
        return step

    def print_last_step(self):
        step = self.get(self.game.state.tutorial_step - 1)
        if step:
            echo_tutorial(step.description)

    def cont(self):
        step = self.get_next_step()
        if step:
            self.game.state.tutorial_step += 1
            self.apply_effects(step)
            self.game.save()
            echo_tutorial(step.description)
            if self.game._messages:
                echo("")
            echo_alerts(self.game)
            return True
