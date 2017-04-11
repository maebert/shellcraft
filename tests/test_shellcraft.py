#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_shellcraft
----------------------------------

Tests for `shellcraft` module.
"""

import os
from click.testing import CliRunner
from shellcraft.shellcraft import Game
from shellcraft import cli


def test_basic_cli():
    runner = CliRunner()
    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "test.json")
    cli.game = Game.create(game_path)
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    print(result.output)
    assert 'Welcome to ShellCraft' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_game_run():
    runner = CliRunner()
    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "test.json")
    cli.game = Game.create(game_path)
    cli.game.flags.debug = True

    commands = """
    mine clay
    mine clay
    mine clay
    mine clay
    craft clay_shovel
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    craft sturdy_clay_shovel
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    research clay_cart
    craft clay_cart
    mine clay
    """
    for command in commands.splitlines():
        runner.invoke(cli.main, command.split())
        print(command, cli.game.resources.clay)
    assert 'clay_cart' in cli.game.flags.research_completed
    assert cli.game.resources.clay == 4
