# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from shellcraft.core import AbstractCollection, AbstractItem
from shellcraft._cli_impl import secho_tutorial


class Step(AbstractItem):
    def __repr__(self):
        return "<Tutorial {}>".format(self.name)


class Tutorial(AbstractCollection):
    FIXTURES = "tutorials.yaml"
    ITEM_CLASS = Step

    def get_next_step(self):
        step = self.get(self.game.flags.tutorial_step)
        if not step or not self.is_available(step):
            return None
        return step

    def print_last_step(self):
        step = self.get(self.game.flags.tutorial_step - 1)
        if step:
            secho_tutorial(step.description)

    def cont(self):
        step = self.get_next_step()
        if step:
            self.game.flags.tutorial_step += 1
            self.apply_effects(step)
            self.game.save()
            secho_tutorial(step.description)
            return True
