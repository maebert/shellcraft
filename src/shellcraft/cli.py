# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import

import click
from shellcraft.shellcraft import Game
from shellcraft._cli_impl import secho, Action, RESOURCE_COLORS
import os

APP_NAME = 'ShellCraft'
GAME_PATH = os.path.join(click.get_app_dir(APP_NAME), 'config.json')
game = Game.load(GAME_PATH) if os.path.exists(GAME_PATH) else Game.create(GAME_PATH)


@click.group()
def main():  # noqa
    """ShellCraft is a command line based crafting game"""
    pass


@main.command()
@click.argument("resource")
def mine(resource):
    """Mine a resource."""
    if not game.flags.resource_available(resource):

        secho("You can't mine {} yet", resource, err=True)
    if game.is_busy:
        secho("You're busy {}ing {}.", game.action.task, game.action.completion, err=True)

    duration, quantity = game.mine(resource)
    game.save()

    action = Action("Mining " + resource, duration, color=RESOURCE_COLORS[resource])
    action.do()
    for m in game._messages:
        secho(m)
    game._messages = []
    secho("Mined *{} {}*", quantity, resource)


@main.command()
@click.argument("item")
def craft(item):
    """Mine a resource."""

    if not game._can_craft(item):
        missing_resources = game._resources_missing_to_craft(item)
        e = "Need {} to craft {}.".format(", ".join("{} {}".format(v, k) for k, v in missing_resources.items()), item)
        secho(e, err=True)

    action = Action("Crafting " + item, 5, color=RESOURCE_COLORS['item'])
    action.do()
    game._craft(item)
    secho("Crafted ${}$", item)
    game.save()


@main.command()
@click.option("--type", help="Only print value for a specific resource, e.g. clay", type=str)
def resources(type=None):
    """Show available resources."""
    if not type:
        for resource in ("clay", "ore", "energy"):
            if game.flags.resource_available(resource):
                secho("*{}: {}*", resource, game.resources.get(resource))
    else:
        if game.flags.resource_available(type):
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
            secho(item)


@main.command()
@click.option("--force", is_flag=True, help="Don't question my orders, just execute them!")
def reset(force):
    """Reset all progress."""
    if force or click.confirm("Do you really want to reset the game and start over again?"):
        Game.create(GAME_PATH).save()
        click.echo("Tabula rasa.")
    else:
        click.echo("Nevermind then.")


if __name__ == "__main__":
    main()
