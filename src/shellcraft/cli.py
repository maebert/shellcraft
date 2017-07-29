# -*- coding: utf-8 -*-

"""Basic CLI for ShellCraft."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click
from shellcraft.shellcraft import Game
from shellcraft._cli_impl import echo, Action, VERBS, echo_alerts, _format_cost, animate_automaton, handle_exception
import datetime
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
        try:
            callback(**kwargs)
            game.complete_missions()
            echo_alerts(game)
            game.tutorial.cont()
            game.save()
        except Exception as e:
            handle_exception(e)
    return inner


def handle_debug(game):
    if sys.argv[2] == "off":  # Disable hyperlapse
        game.flags.debug = False
        echo("Debug mode is `off`")
    elif sys.argv[2] == "on":  # Enable hyperlapse
        game.flags.debug = True
        echo("Debug mode is `on`")
    elif sys.argv[2] == "trigger":  # Trigger an event
        game.events.trigger(sys.argv[3])
    elif sys.argv[2] == "automata":  # Trigger an event
        from shellcraft.automata import Automaton, World
        name = "".join(sys.stdin.readlines())
        w = World(game, 20, 20)
        a = Automaton(name)
        print(a.name.shortcode)
        animate_automaton(a, w)

    echo_alerts(game)
    game.save()


def main(game_path=None):
    game = get_game(game_path)

    # Cheat mode, properly hardcoded.
    if len(sys.argv) > 2 and sys.argv[1] == "debug":
        handle_debug(game)
        sys.exit(0)

    # Remove all commands from the main group that are not enabled in the game yet.
    if not game.state.debug:
        cli.commands = {cmd: command for cmd, command in cli.commands.items() if cmd in game.state.commands_enabled}

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
        if game.state.tutorial_step == 0:
            game.tutorial.cont()
        else:
            echo(ctx.get_help())


@cli.command(options_metavar='')
@click.pass_obj
def contract(game):
    game.add_mission('trade_proposal')
    game.save()


@cli.command(options_metavar='')
@click.argument("resource", metavar='<resource>')
@click.pass_obj
def mine(game, resource):
    """Mine a resource."""
    if resource not in game.state.resources_enabled:
        raise ResourceNotAvailable(resource)


    duration, quantity = game.mine(resource)
    game.save()

    action = Action("mine", resource, duration)
    action.do(skip=game.state.debug)


@cli.command(options_metavar='')
@click.argument("items", nargs=-1, type=str, metavar='<item>')
@click.pass_obj
def craft(game, items):
    """Mine a resource."""
    if len(items) > 1:
        echo("Can only craft one project at a time", err=True)

    elif not items:
        if not game.workshop.available_items:
            echo("There's nothing you can craft right now.", err=True)
        for item in game.workshop.available_items:
            echo("{} ({})\n  {}", item, _format_cost(item.cost), item.description)
    else:
        item = game.workshop.get(items[0])

        if not item:
            echo("No such item", err=True)
            return None

        if not game.workshop.is_available(item):
            echo("{} is not available yet.", item, err=True)
            return None

        if not game.workshop.can_afford(item):
            missing_resources = game.workshop._resources_missing_to_craft(item)
            e = "Need another {} to craft {}.".format(_format_cost(missing_resources), item)
            echo(e, err=True)

        difficulty = game.craft(item)
        game.save()

        action = Action("craft", item, difficulty)
        action.do(skip=game.state.debug)


@cli.command(options_metavar='')
@click.argument("resource_types", nargs=-1, type=str, metavar="<resource>")
@click.pass_obj
def resources(game, resource_types=None):
    """Show available resources."""
    types = resource_types or ("clay", "ore", "energy")
    for resource in types:
        if resource in game.state.resources_enabled:
            echo("*{}: {:.0f}*", resource, game.resources.get(resource))
        elif resource_types:
            echo("*{}* is not available yet.", resource)


@cli.command(options_metavar='')
@click.pass_obj
def inventory(game):
    """Show owned items and their condition."""
    if not game.tools:
        echo("You don't own any items", err=True)
    else:
        for item in game.tools:
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
            dt = game.state.action.completion.ToDatetime() - datetime.datetime.now()
            echo("You're busy {} for another {:.0f} seconds.", VERBS[game.state.action.task], dt.total_seconds(), err=True)

        project = game.lab.get(projects[0])
        if not project:
            echo("No such research project.", err=True)

        if project.name in game.state.research_completed:
            echo("You've already researched {}.", project, err=True)
            return None

        if not game.lab.is_available(project):
            echo("You can't research {} yet.", project, err=True)
            return None

        difficulty = game.research(project)
        game.save()

        action = Action("research", project, difficulty)
        action.do(skip=game.state.debug)


@cli.command(options_metavar='')
@click.option("--force", is_flag=True, help="Don't question my orders, just execute them!")
@click.pass_obj
def reset(game, force):
    """Reset all progress."""
    if force or click.confirm("Do you really want to reset the game and start over again?"):
        Game.create(game.save_file)
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
