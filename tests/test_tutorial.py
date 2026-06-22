"""Tutorial progression."""


def test_first_step_available_on_fresh_game(new_game):
    """tutorial_step starts at 0 and step 0 has no prerequisites."""
    new_game.state.tutorial_step = 0
    step = new_game.tutorial.get_next_step()
    assert step is not None
    assert step.name == "0"


def test_cont_advances_step_and_returns_true(new_game):
    new_game.state.tutorial_step = 0
    advanced = new_game.tutorial.cont()
    assert advanced is True
    assert new_game.state.tutorial_step == 1


def test_cont_returns_false_when_prereq_unmet(new_game):
    """Step 1 needs clay >= 1; without clay the tutorial pauses."""
    new_game.state.tutorial_step = 1
    advanced = new_game.tutorial.cont()
    assert advanced is False
    assert new_game.state.tutorial_step == 1


def test_cont_resumes_once_prereq_met(new_game):
    new_game.state.tutorial_step = 1
    new_game.resources.add("clay", 1)
    assert new_game.tutorial.cont() is True
    assert new_game.state.tutorial_step == 2


def test_print_last_step_does_not_crash(new_game, capsys):
    """After advancing past step 0, print_last_step echoes step 0."""
    new_game.state.tutorial_step = 1
    new_game.tutorial.print_last_step()
    out = capsys.readouterr().out
    assert "ShellCraft" in out


def test_tutorial_step_with_no_predecessor_is_quiet(new_game, capsys):
    """Before any step has been taken, print_last_step prints nothing."""
    new_game.state.tutorial_step = 0
    new_game.tutorial.print_last_step()
    out = capsys.readouterr().out
    assert out == ""
