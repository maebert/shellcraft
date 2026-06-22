# -*- coding: utf-8 -*-
"""Exceptions."""

import datetime
from shellcraft.grammar import VERBS


class ShellcraftException(RuntimeError):
    pass


class BusyException(ShellcraftException):
    """Raised when the player tries to start an action while another is in progress."""

    def __init__(self, game):
        self._time_left = game.state.action.completion - datetime.datetime.now()
        self._action = game.state.action.task
        self._target = game.state.action.target

    def __str__(self):
        from shellcraft.utils import format_duration

        verb = VERBS[self._action]
        target = f" {self._target}" if self._target else ""
        duration = format_duration(self._time_left.total_seconds())
        return f"You're busy {verb}{target} for another {duration}."


class ResourceNotAvailable(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""

    def __init__(self, resource):
        self._resource = resource

    def __str__(self):
        return f"You can't mine {self._resource} yet"
