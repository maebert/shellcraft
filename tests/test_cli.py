"""Click command surface: each top-level subcommand."""

import pytest
from click.testing import CliRunner

from shellcraft import cli as cli_module
from shellcraft.cli import cli
from shellcraft.shellcraft import Game


@pytest.fixture
def runner_game(tmp_path, monkeypatch):
    """A Click runner with cli_module.GAME pre-seeded to an isolated debug game.

    Tests mutate the returned `game` (also installed as `cli_module.GAME`) to set
    up enabled commands/resources before invoking subcommands.
    """
    save_path = tmp_path / "save.json"
    game = Game.create(str(save_path))
    game.state.debug = True
    game.state.action = None

    monkeypatch.setattr(cli_module, "GAME", game)
    return CliRunner(), str(save_path), game


def test_resources_command_lists_unlocked(runner_game):
    runner, _, game = runner_game
    game.state.resources_enabled.append("clay")
    game.resources.add("clay", 7)
    game.state.commands_enabled.append("resources")
    result = runner.invoke(cli, ["resources"])
    assert result.exit_code == 0
    assert "clay" in result.output
    assert "7" in result.output


def test_resources_command_warns_on_locked(runner_game):
    runner, _, game = runner_game
    game.state.commands_enabled.append("resources")
    result = runner.invoke(cli, ["resources", "ore"])
    # The ResourceNotAvailable-style alert routes through echo with err=True.
    assert "not available" in result.output


def test_inventory_empty(runner_game):
    runner, _, game = runner_game
    game.state.commands_enabled.append("inventory")
    result = runner.invoke(cli, ["inventory"])
    assert "don't own any items" in result.output


def test_inventory_with_one_tool(runner_game):
    runner, _, game = runner_game
    game.state.commands_enabled.append("inventory")
    from shellcraft.game_state import ToolInstance

    game.state.tools.append(ToolInstance(name="shovel", condition=16))
    result = runner.invoke(cli, ["inventory"])
    assert "shovel" in result.output


def test_mine_unenabled_resource_rejected(runner_game):
    runner, _, game = runner_game
    game.state.commands_enabled.append("mine")
    result = runner.invoke(cli, ["mine", "energy"])
    # ResourceNotAvailable exception is caught by handle_exception and
    # exits with code 1 via the err=True echo.
    assert result.exit_code != 0 or "yet" in result.output


def test_reset_force_wipes_state(runner_game):
    runner, save_path, game = runner_game
    game.state.commands_enabled.append("reset")
    game.resources.add("clay", 50)
    game.save()

    result = runner.invoke(cli, ["reset", "--force"])
    assert result.exit_code == 0
    assert "Tohu wa-bohu" in result.output


def test_version_flag(runner_game):
    runner, _, _ = runner_game
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "ShellCraft" in result.output


def test_research_while_busy_reports_remaining_time(runner_game):
    """`research X` while another action is in progress must not crash on the
    datetime arithmetic (regression: completion.ToDatetime() was a protobuf-ism)."""
    import datetime

    from shellcraft.game_state import Action

    runner, _, game = runner_game
    game.state.commands_enabled.append("research")
    game.state.resources_enabled.append("clay")
    game.state.research_enabled.append("small_cart")
    game.resources.add("clay", 30)
    # Simulate an in-progress mining action that hasn't completed yet.
    game.state.debug = False
    game.state.action = Action(
        task="mine",
        target="clay",
        completion=datetime.datetime.now() + datetime.timedelta(seconds=5),
    )

    result = runner.invoke(cli, ["research", "small_cart"])
    # err=True echoes call sys.exit(1) so a non-zero exit is expected.
    assert "ToDatetime" not in result.output
    # Message includes the verb, the target, and the human duration.
    assert "mining clay" in result.output
    assert "for another" in result.output
    assert "second" in result.output


def test_help_lists_commands(runner_game):
    runner, _, _ = runner_game
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
