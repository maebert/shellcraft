# -*- coding: utf-8 -*-
"""Exceptions."""

import datetime
from shellcraft.grammar import VERBS


class ShellcraftException(RuntimeError):
    pass


class BusyException(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""

    def __init__(self, game):
        self._time_left = (
            game.state.action.completion.ToDatetime() - datetime.datetime.now()
        )
        self._action = game.state.action.task

    def __str__(self):
        return f"You're busy {VERBS[self._action]} for another { self._time_left.total_seconds():.0f} seconds."


class ResourceNotAvailable(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""

    def __init__(self, resource):
        self._resource = resource

    def __str__(self):
        return f"You can't mine {self._resource} yet"
