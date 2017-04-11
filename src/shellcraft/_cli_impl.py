# -*- coding: utf-8 -*-

"""CLI implementations."""

import click
from click.termui import get_terminal_size
import time
import re
import sys
import textwrap

RESOURCE_COLORS = {
    "clay": 'yellow',
    "ore": 'green',
    "command": 'blue',
    "craft": 'magenta',
    "research": 'green',
}

VERBS = {
    "research": "researching",
    "mine": "mining",
    "craft": "crafting"
}


def secho_tutorial(message):
    """Pretty-print a tutoria step."""
    term_width, _ = get_terminal_size()
    for part in message.splitlines():
        click.echo("")
        part = _format_str(part)
        for line in textwrap.wrap(part, width=term_width - 2):
            if line.startswith("`"):
                line = "\n    " + line + "\n"
            click.echo(line)


def _color_in(match):
    s = match.group(0)
    color = 'white'
    if s.startswith("$"):
        color = RESOURCE_COLORS['craft']
    elif s.startswith("@"):
        color = RESOURCE_COLORS['research']
    elif s.startswith("`"):
        color = RESOURCE_COLORS['command']
    elif s.startswith("*"):
        for res, col in RESOURCE_COLORS.items():
            if res in s:
                color = col
    else:
        color = 'blue'
    return click.style(s.strip("$*@`"), fg=color)


def _format_str(s):
    return re.sub(r'(([\$\*@`])[{};:.a-z0-9_\- ]+(\2))', _color_in, s)


def _unformat_str(s):
    return re.sub(r'(([\$\*@`])([{};:.a-z0-9_\- ]+)(\2))', r"\3", s)


def secho(s, *vals, **kwargs):
    """Echo a string with colours.

    Options are *resource* to highlight a resource, `code` for tutorials.
    """
    if vals:
        s = s.format(*vals)
    if kwargs.get("err"):
        click.secho(_unformat_str(s), fg='red', err=True)
        sys.exit(1)
    else:
        click.echo(_format_str(s))


class Action:
    """Represent an action that takes some time to complete."""

    def __init__(self, action, target, duration):
        """Set up the new action.

        Args:
            action (str): name of the action
            duration (float): duration of the action in seconds
            color (str): color representing the action if progress bar is used.
        """
        self.duration = duration
        self.color = RESOURCE_COLORS[target] if action == "mine" else RESOURCE_COLORS[action]
        target_str = "*{}*".format(target) if action == 'mine' else target
        self.action = _format_str("{} {}".format(VERBS[action], target_str).capitalize())
        self.elapsed = 0.

    def _eta(self):
        """Friendly formatted ETA."""
        t = self.duration - self.elapsed
        if t < 1:
            return "{:.2f}s".format(t)
        elif t < 60:
            return "{:.0f}s".format(t)
        elif t < 3600:
            return "{:.0f}m {:.0f}s".format(t // 60, t % 60)
        else:
            return "{:.0f}h {:.0f}m".format(t // 3600, (t % 3600) / 60)

    def draw(self):
        """Echo the current progress bar."""
        term_width, _ = get_terminal_size()
        bar_width = term_width - len(self.action) - 20
        blocks = min(bar_width, int(self.elapsed / self.duration * bar_width))
        remaining = bar_width - blocks
        info = self._eta()
        bar = "\r{} {}{} {:<18}".format(
            self.action,
            click.style('▓' * blocks, fg=self.color),
            '░' * remaining,
            info
        )
        click.echo(bar, nl=False)

    def do(self, skip=False):
        """Start the action."""
        if skip:
            return
        term_width, _ = get_terminal_size()
        blocks = (term_width - len(self.action) - 20.0)
        delta = self.duration / blocks
        while self.elapsed < self.duration:
            self.draw()
            time.sleep(delta)
            self.elapsed += delta
        term_width, _ = get_terminal_size()
        click.echo("\r" + " " * (term_width - 1) + "\r", nl=False)
