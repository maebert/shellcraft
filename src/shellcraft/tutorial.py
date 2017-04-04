# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
import os
import yaml
import sys
from shellcraft._cli_impl import secho_tutorial


class Tutorial:
    def __init__(self, game):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tutorials.yaml")) as f:
            self.steps = yaml.load(f)
        self.game = game

    def get_next_step(self):
        next_step = self.game.flags.tutorial_step
        step = self.steps.get(next_step)
        if not step:
            return None
        if 'required_resources' in step:
            if not all(self.game.resources.get(res) >= res_cost for res, res_cost in step['required_resources'].items()):
                return None
        if 'required_items' in step:
            if not all(self.game._get_item(item) for item in step['required_items']):
                return None
        return step['message']

    def print_last_step(self):
        step = self.steps.get(self.game.flags.tutorial_step - 1)
        if step:
            secho_tutorial(step['message'])

    def cont(self):
        step = self.get_next_step()
        if step:
            self.game.flags.tutorial_step += 1
            self.game.save()
            secho_tutorial(step)
            return True
