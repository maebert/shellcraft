# -*- coding: utf-8 -*-

"""CLI implementations."""
from __future__ import absolute_import, division, print_function, unicode_literals

from shellcraft.grammar import Grammar, VERBS
from shellcraft._colors import Color, Gradient
import click
from click.termui import get_terminal_size
import time
import re
import sys
import textwrap
from future.moves.itertools import zip_longest

RESOURCE_COLORS = {
    "clay": Color.yellow,
    "ore": Color.green,
    "command": Color.grey,
    "craft": Color.purple,
    "research": Color.blue,
    "automata": Color.pink
}


def handle_exception(e):
    """Echo error message and shut down.

    Args:
        e: Exception
    """
    echo(str(e), err=True)


def alen(s):
    """Length of a string without ANSI characters."""
    return len(s) - len("".join(re.findall(r"((?:\x1b|\033)\[[\d:;]+m)", s)))


def grid_echo(*cols):
    """Align columns into a grid and echo.

    Args:
        cols: str - columns to print
    Returns:
        int - max height
    """
    cols = [box(col, join=False) for col in cols]
    col_lengths = [max(map(alen, col)) for col in cols]
    line_fmt = "{:{}}" * len(cols)
    for parts in zip_longest(*cols, fillvalue=""):
        values = [j for i in zip(parts, col_lengths) for j in i]
        line = line_fmt.format(*values)
        click.echo(line)
    click.echo()
    return max(map(len, cols))


def box(s, join=True):
    """Draw a box around a string.

    Args:
        s: str
        join: bool - if true, return a string. Else, return list of lines.
    """
    lines = s.splitlines()
    w = max(map(alen, lines))
    result = ["╭" + "─" * w + "╮"]
    result += ["│{:{}}│".format(line, w) for line in lines]
    result += ["╰" + "─" * w + "╯"]
    if join:
        return "\n".join(result)
    return result


def draw_world(world, automaton, w, h):
    def _field(**resources):
        clay = resources.get('clay', 0)
        ore = resources.get('ore', 0)
        elevation = resources.get('elevation', 0)
        if ore:
            return Gradient.green('█', ore)
        elif clay:
            return Gradient.yellow('█', clay)
        else:
            return Gradient.dark("█", elevation)

    result = []
    x, y = automaton.x, automaton.y

    for py in range(y - h // 2, y + h // 2 + 1):
        row = ''
        for px in range(x - w // 2, x + w // 2 + 1):
            if px == x and py == y:
                row += RESOURCE_COLORS['automata']("▲▶▼◀︎"[automaton.direction])
            else:
                row += _field(**world.get_resources(px, py))
        result.append(row)
    return "\n".join(result)


def draw_automaton_state(automaton):
    s = ""
    for line in automaton.name._cells:
        for cell in line:
            s += click.style(cell.symbol.strip() or "·", bg=[None, 'yellow', 'red'][cell.state])
        s += "\n"
    return s


def animate_automaton(automaton, world):
    while True:
        automaton.step()
        a = draw_automaton_state(automaton)
        w = draw_world(world, automaton, 15, 9)
        height = grid_echo(a, w)
        time.sleep(1)
        click.echo("\x1b[{}A".format(height + 2))


def echo_alerts(game):
    """Display all alerts that are currently queued up."""
    for m in game._messages:
        echo(m, use_cursor=True)
    game._messages = []


def echo_tutorial(message):
    """Pretty-print a tutoria step."""
    term_width, _ = get_terminal_size()
    for part in message.splitlines():
        click.echo("")
        part = _format_str(part)
        for line in textwrap.wrap(part, width=min(60, term_width - 2)):
            if line.startswith("`"):
                line = "\n    " + line + "\n"
            click.echo(line)


def _color_in(match):
    s = match.group(0)
    color = Color.white
    if s.startswith("$"):
        color = RESOURCE_COLORS['craft']
    elif s.startswith("%"):
        color = RESOURCE_COLORS['research']
    elif s.startswith("`"):
        color = RESOURCE_COLORS['command']
    elif s.startswith("*"):
        for res, col in RESOURCE_COLORS.items():
            if res in s:
                color = col
    else:
        color = Color.grey
    return color(s.strip("$*%`"))


def _format_str(s):
    return re.sub(r'(([\$\*%`])[{};:.a-z0-9_\- ]+(\2))', _color_in, s)


def _unformat_str(s):
    return re.sub(r'(([\$\*%`])([{};:.a-z0-9_\- ]+)(\2))', r"\3", s)


def _format_cost(cost):
    return ", ".join("*{} {}*".format(v, k) for k, v in cost.items())


def ask(msg):
    """Show a confirmation prompt."""
    return click.confirm("❯ " + _format_str(msg))


def echo(s, *vals, **kwargs):
    """Echo a string with colours.

    Args:
        err (bool): If True, print to stderr
        use_cursor (bool): If True, use interaction cursor
    """
    if vals:
        s = s.format(*vals)

    err = kwargs.pop("err", False)
    use_cursor = kwargs.pop("use_cursor", False)

    grammar_match = re.search("^~([a-zA-Z0-9_]+)~ *", s)
    if grammar_match:
        grammar_name = grammar_match.group(1)
        s = s[grammar_match.end():]
        grammar = Grammar.grammars[grammar_name]
        s = grammar.generate(s)
    if use_cursor:
        s = "❯ " + s

    result = ""
    for line in s.splitlines():
        if not line.startswith(">"):
            result += line + "\n"
        else:
            # Format letter

            line = line.replace("> ", "\n")
            w = min(50, get_terminal_size()[0] - 12)
            result += Color.grey("    ╭┄┬┄" + "┄" * w + "┄╮\n")
            result += Color.grey("    ╰┄┤ " + " " * w + " ┊\n")
            for paragraph in filter(bool, line.splitlines()):
                for l in textwrap.wrap(paragraph, width=w, replace_whitespace=False):
                    result += Color.grey("      ┊ ") + l
                    result += " " * (w - len(_unformat_str(l))) + Color.grey(" ┊\n")
                result += Color.grey("      ┊ " + " " * w + " ┊\n")
            result += Color.grey("      ┊ ╭" + "┄" * w + "┴┄╮\n")
            result += Color.grey("      ╰┄┴" + "┄" * w + "┄┄╯\n")

    if err:
        click.echo(Color.red(_unformat_str(result)), err=True)
        sys.exit(1)
    else:
        click.echo(_format_str(result))


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
        self.dark_color = self.color.mix(Color.dark, .7)
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
        bar_width = term_width - len(self.action) - 10
        blocks = min(bar_width, int(self.elapsed / self.duration * bar_width))
        remaining = bar_width - blocks
        info = self._eta()
        bar = "\r{} {}{} {:<18}".format(
            self.action,
            self.color('█' * blocks),
            self.dark_color('░' * remaining),
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
