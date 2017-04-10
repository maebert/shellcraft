# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import

import click
from shellcraft.shellcraft import Game
from shellcraft.tutorial import Tutorial
from shellcraft._cli_impl import secho, Action, RESOURCE_COLORS
import os

APP_NAME = 'ShellCraft'
GAME_PATH = os.path.join(click.get_app_dir(APP_NAME), 'config.json')

game = Game.load(GAME_PATH) if os.path.exists(GAME_PATH) else Game.create(GAME_PATH)
TUTORIAL = Tutorial(game)


def action_step(callback):
    def inner(**kwargs):
        # Do the action
        callback(**kwargs)
        for m in game._messages:
            secho("❯ " + m)
        game._messages = []
        TUTORIAL.cont()
    return inner


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):  # noqa
    """ShellCraft is a command line based crafting game."""
    if ctx.invoked_subcommand is None:
        has_tut = TUTORIAL.cont()
        if not has_tut:
            click.echo("Use shellcraft --help to see a list of available commands.")


@main.command()
@click.argument("resource", metavar='<resource>')
def mine(resource):
    """Mine a resource."""
    if resource not in game.flags.resources_enabled:

        secho("You can't mine {} yet", resource, err=True)
    if game.is_busy:
        secho("You're busy {}ing {}.", game.action.task, game.action.completion, err=True)

    duration, quantity = game.mine(resource)
    game.save()

    action = Action("Mining *{}*".format(resource), duration, color=RESOURCE_COLORS[resource])
    action.do()


@main.command()
@click.argument("item", metavar='<item>')
def craft(item):
    """Mine a resource."""
    item = game.tools.get(item)

    if not item:
        secho("No such item", err=True)
        return None

    if not game.tools.is_available(item):
        secho("{} is not available yet.", item, err=True)
        return None

    if not game.tools.can_afford(item):
        missing_resources = game.tools._resources_missing_to_craft(item)
        e = "Need {} to craft {}.".format(", ".join("{} {}".format(v, k) for k, v in missing_resources.items()), item)
        secho(e, err=True)

    action = Action("Crafting {}".format(str(item)), 5, color=RESOURCE_COLORS['item'])
    action.do()
    game.craft(item)
    game.save()


@main.command()
@click.option("--type", help="Only print value for a specific resource, e.g. clay", type=str, metavar="<resource>")
def resources(type=None):
    """Show available resources."""
    if not type:
        for resource in ("clay", "ore", "energy"):
            if resource in game.flags.resources_enabled:
                secho("*{}: {}*", resource, game.resources.get(resource))
    else:
        if type in game.flags.resources_enabled:
            secho("*{}: {:<5d}*", type, game.resources.get(type))
        else:
            secho("{} is not available yet.", type)


@main.command()
def inventory():
    """Show owned items and their condition."""
    if not game.items:
        secho("You don't own any items", err=True)
    else:
        for item in game.items:
            secho(str(item))
            # secho("${}$ ({:.0%})", item.name, item.condition / item.durability)


@main.command()
@click.option("--force", is_flag=True, help="Don't question my orders, just execute them!")
def reset(force):
    """Reset all progress."""
    if force or click.confirm("Do you really want to reset the game and start over again?"):
        Game.create(GAME_PATH).save()
        click.echo("Tabula rasa.")
    else:
        click.echo("Nevermind then.")


@main.command()
def tutorial():
    """Print the last step of the tutorial."""
    TUTORIAL.print_last_step()

# This removes all commands from the main group that are not enabled
# in the game yet.
main.commands = {cmd: command for cmd, command in main.commands.items() if cmd in game.flags.commands_enabled}

for cmd in ('mine', 'craft'):
    if cmd in main.commands:
        main.commands[cmd].callback = action_step(main.commands[cmd].callback)

if __name__ == "__main__":
    main()
