# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import
from __future__ import unicode_literals

import click
from shellcraft.shellcraft import Game
from shellcraft._cli_impl import echo, Action, VERBS, echo_alerts, _format_cost
import os
import sys

click.disable_unicode_literals_warning = True

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
        echo_alerts(game)
        game.tutorial.cont()
    return inner


def main(game_path=None):
    game = get_game(game_path)

    # Cheat mode, properly hardcoded.
    if sys.argv[-1] == "debug":
        game.flags.debug = not game.flags.debug
        game.save()
        echo("Debug mode is " + ("$on$" if game.flags.debug else "`off`"))
        sys.exit(0)

    # Remove all commands from the main group that are not enabled in the game yet.
    cli.commands = {cmd: command for cmd, command in cli.commands.items() if cmd in game.flags.commands_enabled}

    for cmd in ('mine', 'craft', 'research'):
        if cmd in cli.commands:
            cli.commands[cmd].callback = action_step(cli.commands[cmd].callback, game)
    cli()


@click.group(invoke_without_command=True, options_metavar='', subcommand_metavar='<command>')
@click.pass_context
def cli(ctx):
    """ShellCraft is a command line based crafting game."""
    ctx.obj = game = get_game()

    if ctx.invoked_subcommand is None:
        if game.flags.tutorial_step == 0:
            game.tutorial.cont()
        else:
            echo(ctx.get_help())


@cli.command(options_metavar='')
@click.pass_obj
def contract(game):
    from shellcraft.events import Contract
    c = Contract(game)
    c.offer()


@cli.command(options_metavar='')
@click.argument("resource", metavar='<resource>')
@click.pass_obj
def mine(game, resource):
    """Mine a resource."""
    if resource not in game.flags.resources_enabled:
        echo("You can't mine {} yet", resource, err=True)

    duration, quantity = game.mine(resource)
    game.save()

    action = Action("mine", resource, duration)
    action.do(skip=game.flags.debug)


@cli.command(options_metavar='')
@click.argument("items", nargs=-1, type=str, metavar='<item>')
@click.pass_obj
def craft(game, items):
    """Mine a resource."""
    if len(items) > 1:
        echo("Can only craft one project at a time", err=True)

    elif not items:
        if not game.tools.available_items:
            echo("There's nothing you can craft right now.", err=True)
        for item in game.tools.available_items:
            echo("{} ({})\n  {}", item, _format_cost(item.cost), item.description)
    else:
        item = game.tools.get(items[0])

        if not item:
            echo("No such item", err=True)
            return None

        if not game.tools.is_available(item):
            echo("{} is not available yet.", item, err=True)
            return None

        if not game.tools.can_afford(item):
            missing_resources = game.tools._resources_missing_to_craft(item)
            e = "Need {} to craft {}.".format(_format_cost(missing_resources), item)
            echo(e, err=True)

        difficulty = game.craft(item)
        game.save()

        action = Action("craft", item, difficulty)
        action.do(skip=game.flags.debug)


@cli.command(options_metavar='')
@click.argument("resource_types", nargs=-1, type=str, metavar="<resource>")
@click.pass_obj
def resources(game, resource_types=None):
    """Show available resources."""
    types = resource_types or ("clay", "ore", "energy")
    for resource in types:
        if resource in game.flags.resources_enabled:
            echo("*{}: {}*", resource, game.resources.get(resource))
        elif resource_types:
            echo("*{}* is not available yet.", resource)


@cli.command(options_metavar='')
@click.pass_obj
def inventory(game):
    """Show owned items and their condition."""
    if not game.items:
        echo("You don't own any items", err=True)
    else:
        for item in game.items:
            echo(str(item))
            # echo("${}$ ({:.0%})", item.name, item.condition / item.durability)


@cli.command(options_metavar='')
@click.argument("projects", nargs=-1, type=str, metavar="<project>")
@click.pass_obj
def research(game, projects):
    """Show owned items and their condition."""
    if len(projects) > 1:
        echo("Can only research one project at a time", err=True)

    elif not projects:
        for item in game.lab.available_items:
            echo("{} ({} sec)\n  {}", item, item.difficulty, item.description)
        if not game.lab.available_items:
            echo("There are currently no projects available for research.", err=True)
    else:
        # Researching something now
        if game.is_busy:
            echo("You're busy {} until {}.", VERBS[game.action.task], game.action.completion, err=True)

        project = game.lab.get(projects[0])
        if not project:
            echo("No such research project.", err=True)

        if project.name in game.flags.research_completed:
            echo("You've already researched {}.", project, err=True)
            return None

        if not game.lab.is_available(project):
            echo("You can't research {} yet.", project, err=True)
            return None

        difficulty = game.research(project)
        game.save()

        action = Action("research", project, difficulty)
        action.do(skip=game.flags.debug)


@cli.command(options_metavar='')
@click.option("--force", is_flag=True, help="Don't question my orders, just execute them!")
@click.pass_obj
def reset(game, force):
    """Reset all progress."""
    if force or click.confirm("Do you really want to reset the game and start over again?"):
        Game.create(game.save_file).save()
        echo("Tohu wa-bohu.")
    else:
        echo("Nevermind then.")


@cli.command()
@click.pass_obj
def tutorial(game):
    """Print the last step of the tutorial."""
    game.tutorial.print_last_step()


if __name__ == "__main__":
    main()
