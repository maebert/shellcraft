#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_shellcraft.

Tests for `shellcraft` module.
"""

from __future__ import unicode_literals

import os
import pytest
from click.testing import CliRunner
from shellcraft.cli import get_game, cli
from shellcraft.shellcraft import Game


@pytest.fixture(scope='module')
def game():
    """Create a local game."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        game = get_game("test.json")
    return game


def load_game(filename):
    """Load game from fixtures."""
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", filename)
    print(filename)
    return Game.load(filename)


def test_basic_cli(game):
    """Test that the interface loads."""
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert 'Welcome to ShellCraft' in result.output

    help_result = runner.invoke(cli, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_contract(game):
    game = load_game("save1.json")
    assert game.resources.get("clay") == 30


def test_game_run(game):
    """Test that the basic game flow works."""
    commands = """
    mine clay
    mine clay
    mine clay
    mine clay
    craft shovel
    mine clay
    mine clay
    mine clay
    mine clay
    mine clay
    craft sturdy_shovel
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
    research small_cart
    craft small_cart
    mine clay"""
    runner = CliRunner()
    game.state.debug = True
    for command in commands.splitlines():
        assert not command or command.split()[0] in list(game.state.commands_enabled), "{} not in {}".format(command.split()[0], list(game.state.commands_enabled))
        runner.invoke(cli, command.split())
        game.tutorial.cont()
    assert 'small_cart' in game.state.research_completed
    assert game.state.tutorial_step == 11
    assert game.resources.get("clay") == 4
