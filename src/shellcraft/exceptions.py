# -*- coding: utf-8 -*-
"""Exceptions."""

import datetime
from typing import TYPE_CHECKING

from shellcraft.grammar import VERBS

if TYPE_CHECKING:
    from shellcraft.shellcraft import Game


class ShellcraftException(RuntimeError):
    pass


class BusyException(ShellcraftException):
    """Raised when the player tries to start an action while another is in progress."""

    def __init__(self, game: "Game") -> None:
        action = game.state.action
        assert action is not None and action.completion is not None, (
            "BusyException raised when no action in progress"
        )
        self._time_left = action.completion - datetime.datetime.now()
        self._action = action.task
        self._target = action.target

    def __str__(self) -> str:
        from shellcraft.utils import format_duration

        verb = VERBS[self._action]
        target = f" {self._target}" if self._target else ""
        duration = format_duration(self._time_left.total_seconds())
        return f"You're busy {verb}{target} for another {duration}."


class ResourceNotAvailable(ShellcraftException):
    """Exception that is raised if the parse tree runs too deep."""

    def __init__(self, resource: str) -> None:
        self._resource = resource

    def __str__(self) -> str:
        return f"You can't mine {self._resource} yet"
