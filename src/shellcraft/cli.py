# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from __future__ import unicode_literals

import click
from shellcraft.shellcraft import Game
from shellcraft._cli_impl import secho, Action, VERBS
import os

APP_NAME = 'ShellCraft'
GAME = None


def get_game(path=None):
    global GAME
    if GAME:
        return GAME
    path = path or os.path.join(click.get_app_dir(APP_NAME), 'config.json')
    GAME = Game.load(path) if os.path.exists(path) else Game.create(path)
    return GAME


def action_step(callback, game):
    """Wrapper around actions."""
    def inner(**kwargs):
        # Do the action
        callback(**kwargs)
        for m in game._messages:
            secho("❯ " + m)
        game._messages = []
        game.tutorial.cont()
    return inner


def main(game_path=None):
    game = get_game(game_path)

    # Remove all commands from the main group that are not enabled in the game yet.
    cli.commands = {cmd: command for cmd, command in cli.commands.items() if cmd in game.flags.commands_enabled}

    for cmd in ('mine', 'craft', 'research'):
        if cmd in cli.commands:
            cli.commands[cmd].callback = action_step(cli.commands[cmd].callback, game)
    cli()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """ShellCraft is a command line based crafting game."""
    ctx.obj = game = get_game()

    if ctx.invoked_subcommand is None:
        has_tut = game.tutorial.cont()
        if not has_tut:
            click.echo("Use shellcraft --help to see a list of available commands.")


@cli.command()
@click.argument("resource", metavar='<resource>')
@click.pass_obj
def mine(game, resource):
    """Mine a resource."""
    if resource not in game.flags.resources_enabled:
        secho("You can't mine {} yet", resource, err=True)

    duration, quantity = game.mine(resource)
    game.save()

    action = Action("mine", resource, duration)
    action.do(skip=game.flags.debug)


@cli.command()
@click.argument("item", metavar='<item>')
@click.pass_obj
def craft(game, item):
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

    difficulty = game.craft(item)
    game.save()

    action = Action("craft", item, difficulty)
    action.do(skip=game.flags.debug)


@cli.command()
@click.argument("resource_types", nargs=-1, type=str, metavar="<resource>")
@click.pass_obj
def resources(game, resource_types=None):
    """Show available resources."""
    types = resource_types or ("clay", "ore", "energy")
    for resource in types:
        if resource in game.flags.resources_enabled:
            secho("*{}: {}*", resource, game.resources.get(resource))
        elif resource_types:
            secho("*{}* is not available yet.", resource)


@cli.command()
@click.pass_obj
def inventory(game):
    """Show owned items and their condition."""
    if not game.items:
        secho("You don't own any items", err=True)
    else:
        for item in game.items:
            secho(str(item))
            # secho("${}$ ({:.0%})", item.name, item.condition / item.durability)


@cli.command()
@click.argument("projects", nargs=-1, type=str, metavar="<project>")
@click.pass_obj
def research(game, projects):
    """Show owned items and their condition."""
    if len(projects) > 1:
        secho("Can only research one project at a time", err=True)

    elif not projects:
        for item in game.lab.available_items:
            secho("{} {} ({} sec)", item, item.description, item.difficulty)
        if not game.lab.available_items:
            secho("There are currently no projects available for research.", err=True)
    else:
        # Researching something now
        if game.is_busy:
            secho("You're busy {} until {}.", VERBS[game.action.task], game.action.completion, err=True)

        project = game.lab.get(projects[0])
        if not project:
            secho("No such research project.", err=True)

        if project.name in game.flags.research_completed:
            secho("You've already researched {}.", project, err=True)
            return None

        if not game.lab.is_available(project):
            secho("You can't research {} yet.", project, err=True)
            return None

        difficulty = game.research(project)
        game.save()

        action = Action("research", project, difficulty)
        action.do(skip=game.flags.debug)


@cli.command()
@click.option("--force", is_flag=True, help="Don't question my orders, just execute them!")
@click.pass_obj
def reset(game, force):
    """Reset all progress."""
    if force or click.confirm("Do you really want to reset the game and start over again?"):
        Game.create(game.save_file).save()
        secho("Tohu wa-bohu.")
    else:
        secho("Nevermind then.")


@cli.command()
@click.pass_obj
def tutorial(game):
    """Print the last step of the tutorial."""
    game.tutorial.print_last_step()


if __name__ == "__main__":
    main()
