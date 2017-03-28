# -*- coding: utf-8 -*-

"""CLI implementations."""

import click
from click.termui import get_terminal_size
import time

RESOURCE_COLORS = {
    "clay": 'yellow',
    "ore": 'green',
    "energy": 'cyan',
    "item": 'magenta',
}


def fmt_res(resource, n=None):
    """Return a colorised resource string."""
    s = "{} {}".format(n, resource) if n else resource
    return click.style(s, fg=RESOURCE_COLORS[resource])


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


def resource_string(game):
    parts = []
    for resource in ("clay", "ore", "energy"):
        if game.flags.resource_available(resource):
            line = "{}: {:<5d}".format(resource, game.resources.get(resource))
            parts.append(click.style(line, fg=RESOURCE_COLORS[resource]))
    return "\n".join(parts)
