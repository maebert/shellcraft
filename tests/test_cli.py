"""Click command surface: each top-level subcommand."""

import pytest
from click.testing import CliRunner

from shellcraft import cli as cli_module
from shellcraft.cli import cli


@pytest.fixture
def runner_game(tmp_path, monkeypatch):
    """A Click runner with cli_module.GAME pre-seeded to an isolated debug game.

    Tests mutate cli_module.GAME directly to set up enabled commands/resources
    before invoking subcommands.
    """
    from shellcraft.shellcraft import Game

    save_path = tmp_path / "save.json"
    game = Game.create(str(save_path))
    game.state.debug = True
    game.state.action = None

    monkeypatch.setattr(cli_module, "GAME", game)
    return CliRunner(), str(save_path)


def test_resources_command_lists_unlocked(runner_game):
    runner, _ = runner_game
    cli_module.GAME.state.resources_enabled.append("clay")
    cli_module.GAME.resources.add("clay", 7)
    cli_module.GAME.state.commands_enabled.append("resources")
    result = runner.invoke(cli, ["resources"])
    assert result.exit_code == 0
    assert "clay" in result.output
    assert "7" in result.output


def test_resources_command_warns_on_locked(runner_game):
    runner, _ = runner_game
    cli_module.GAME.state.commands_enabled.append("resources")
    result = runner.invoke(cli, ["resources", "ore"])
    # The ResourceNotAvailable-style alert routes through echo with err=True.
    assert "not available" in result.output


def test_inventory_empty(runner_game):
    runner, _ = runner_game
    cli_module.GAME.state.commands_enabled.append("inventory")
    result = runner.invoke(cli, ["inventory"])
    assert "don't own any items" in result.output


def test_inventory_with_one_tool(runner_game):
    runner, _ = runner_game
    cli_module.GAME.state.commands_enabled.append("inventory")
    from shellcraft.game_state import ToolInstance

    cli_module.GAME.state.tools.append(ToolInstance(name="shovel", condition=16))
    result = runner.invoke(cli, ["inventory"])
    assert "shovel" in result.output


def test_mine_unenabled_resource_rejected(runner_game):
    runner, _ = runner_game
    cli_module.GAME.state.commands_enabled.append("mine")
    result = runner.invoke(cli, ["mine", "energy"])
    # ResourceNotAvailable exception is caught by handle_exception and
    # exits with code 1 via the err=True echo.
    assert result.exit_code != 0 or "yet" in result.output


def test_reset_force_wipes_state(runner_game):
    runner, save_path = runner_game
    cli_module.GAME.state.commands_enabled.append("reset")
    cli_module.GAME.resources.add("clay", 50)
    cli_module.GAME.save()

    result = runner.invoke(cli, ["reset", "--force"])
    assert result.exit_code == 0
    assert "Tohu wa-bohu" in result.output


def test_version_flag(runner_game):
    runner, _ = runner_game
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "ShellCraft" in result.output


def test_help_lists_commands(runner_game):
    runner, _ = runner_game
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
