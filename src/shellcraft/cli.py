# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import

import click
from shellcraft.shellcraft import Game
import shellcraft._cli_impl as cli_impl
import os
import sys

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
        click.secho("You can't mine {} yet".format(resource), fg='red', err=True)
        sys.exit(1)
    if game.is_busy:
        click.secho("You're busy {}ing {}.".format(game.action.task, game.action.completion), fg='red', err=True)
        sys.exit(1)

    duration, quantity = game.mine(resource)
    game.save()

    action = cli_impl.Action("Mining " + resource, duration, color=cli_impl.RESOURCE_COLORS[resource])
    action.do()
    for m in game._messages:
        click.echo(m)
    game._messages = []
    click.echo("Mined " + cli_impl.fmt_res(resource, quantity))


@main.command()
@click.argument("item")
def craft(item):
    """Mine a resource."""

    if not game._can_craft(item):
        missing_resources = game._resources_missing_to_craft(item)
        e = "Need {} to craft.".format(", ".join("{} {}".format(v, k) for k, v in missing_resources.items()))
        click.secho(e, fg='red', err=True)
        sys.exit(1)

    action = cli_impl.Action("Crafting " + item, 5, color=cli_impl.RESOURCE_COLORS['item'])
    action.do()
    game._craft(item)
    click.echo("Crafted " + click.style(item, fg=cli_impl.RESOURCE_COLORS['item']))
    game.save()


@main.command()
@click.option("--type", help="Only print value for a specific resource, e.g. clay", type=str)
def resources(type=None):
    """Show available resources."""
    if not type:
        click.echo(cli_impl.resource_string(game))
    else:
        click.echo(game.resources.get(type))


@main.command()
def inventory():
    """Show owned items and their condition."""
    if not game.items:
        click.secho("You don't own any items", fg='red', err=True)
    else:
        for item in game.items:
            click.echo(item)


if __name__ == "__main__":
    main()
