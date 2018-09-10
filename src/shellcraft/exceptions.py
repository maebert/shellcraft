# -*- coding: utf-8 -*-
"""Exceptions."""

from __future__ import absolute_import, division, print_function, unicode_literals
import datetime
from shellcraft.grammar import VERBS


class ShellcraftException(RuntimeError):
    pass


class BusyException(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""
    def __init__(self, game):
        self._time_left = game.state.action.completion.ToDatetime() - datetime.datetime.now()
        self._action = game.state.action.task

    def __str__(self):
        return "You're busy {} for another {:.0f} seconds.".format(VERBS[self._action], self._time_left.total_seconds())


class ResourceNotAvailable(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""
    def __init__(self, resource):
        self._resource = resource

    def __str__(self):
        return "You can't mine {} yet".format(self._resource)
