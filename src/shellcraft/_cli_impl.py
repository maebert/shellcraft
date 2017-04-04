# -*- coding: utf-8 -*-

"""CLI implementations."""

import click
from click.termui import get_terminal_size
import time
import re
import sys

RESOURCE_COLORS = {
    "clay": 'yellow',
    "ore": 'green',
    "energy": 'cyan',
    "item": 'magenta',
}


def _color_in(match):
    s = match.group(0)
    color = 'white'
    if s.startswith("$"):
        color = 'magenta'
    elif s.startswith("*"):
        for res, col in RESOURCE_COLORS.items():
            if res in s:
                color = col
    else:
        color = 'blue'
    return click.style(s.strip("$*`"), fg=color)


def secho(s, *vals, **kwargs):
    """Echo a string with colours.

    Options are *resource* to highlight a resource, `code` for tutorials.
    """
    s = s.format(*vals)
    if kwargs.get("err"):
        click.secho(s, fg='red', err=True)
        sys.exit(1)
    else:
        s = re.sub(r'(([\$\*`])[:.a-z0-9_\- ]+(\2))', _color_in, s)
        click.echo(s)


class Action:
    """Represent an action that takes some time to complete."""

    def __init__(self, action, duration, color='yellow'):
        """Set up the new action.

        Args:
            action (str): name of the action
            duration (float): duration of the action in seconds
            color (str): color representing the action if progress bar is used.
        """
        self.action = action
        self.duration = duration
        self.color = color
        self.elapsed = 0.

    def _eta(self):
        """Friendly formatted ETA."""
        t = self.duration - self.elapsed
        if t < 1:
            return "{:.2f}s".format(t)
        elif t < 60:
            return "{:.0f}s".format(t)
        elif t < 3600:
            return "{:.0f}m {:.0f}s".format(t / 60, t % 60)
        else:
            return "{:.0f}h {:.0f}m".format(t / 3600, (t % 3600) / 60)

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

    def do(self):
        """Start the action."""
        term_width, _ = get_terminal_size()
        blocks = (term_width - len(self.action) - 20.0)
        delta = self.duration / blocks
        while self.elapsed < self.duration:
            self.draw()
            time.sleep(delta)
            self.elapsed += delta
        term_width, _ = get_terminal_size()
        click.echo("\r" + " " * (term_width - 1) + "\r", nl=False)

