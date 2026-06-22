"""Mission lifecycle: serialization, acceptance, completion, failure."""

import datetime

import pytest

from shellcraft import missions as missions_module
from shellcraft.game_state import MissionInstance


@pytest.fixture
def mission_game(new_game):
    """Game ready to accept a trade_proposal: two resources unlocked + stock."""
    new_game.state.resources_enabled.extend(["clay", "ore"])
    new_game.resources.add("clay", 30)
    new_game.resources.add("ore", 10)
    new_game.state.commands_enabled.append("contract")
    return new_game


@pytest.fixture
def auto_accept(monkeypatch):
    """Make the interactive offer prompt always accept."""
    monkeypatch.setattr(missions_module, "ask", lambda *a, **k: True)


@pytest.fixture
def auto_reject(monkeypatch):
    monkeypatch.setattr(missions_module, "ask", lambda *a, **k: False)


def test_mission_instance_roundtrip(tmp_path):
    """A MissionInstance saves and loads via JSON without loss."""
    deadline = datetime.datetime(2026, 6, 30, 12, 0, 0)
    mission = MissionInstance(
        name="trade_proposal",
        demand=10,
        reward=5,
        demand_type="clay",
        reward_type="ore",
        due=60,
        deadline=deadline,
    )
    payload = mission.model_dump_json()
    revived = MissionInstance.model_validate_json(payload)
    assert revived.name == "trade_proposal"
    assert revived.demand == 10
    assert revived.deadline == deadline


def test_mission_template_property_returns_catalog(tmp_path):
    """An instance's `.template` resolves to the catalog entry."""
    mission = MissionInstance(name="trade_proposal")
    template = mission.template
    assert template.name == "trade_proposal"
    assert "intro" in template.strings


def test_accepted_mission_appended_to_state(mission_game, auto_accept):
    accepted = mission_game.add_mission("trade_proposal")
    assert accepted is not None
    assert len(mission_game.state.missions) == 1
    assert mission_game.state.missions[0].name == "trade_proposal"
    # Acceptance stamps a deadline.
    assert mission_game.state.missions[0].deadline is not None


def test_rejected_mission_is_not_persisted(mission_game, auto_reject):
    rejected = mission_game.add_mission("trade_proposal")
    assert rejected is None
    assert mission_game.state.missions == []
    # Rejection dings reputation.
    assert mission_game.state.trade_reputation < 0


def test_mission_completion_pays_reward(mission_game, auto_accept):
    """When resources meet demand, completion exchanges them for the reward."""
    mission_game.add_mission("trade_proposal")
    [mission] = mission_game.state.missions

    # Force a known demand/reward so the test is deterministic.
    mission.demand = 5
    mission.demand_type = "clay"
    mission.reward = 3
    mission.reward_type = "ore"

    clay_before = mission_game.resources.get("clay")
    ore_before = mission_game.resources.get("ore")
    mission_game.complete_missions()

    assert mission_game.state.missions == []
    assert mission_game.resources.get("clay") == clay_before - 5
    assert mission_game.resources.get("ore") == ore_before + 3


def test_mission_failure_when_deadline_passes(mission_game, auto_accept):
    """A mission past its deadline (and unmet) is removed without reward."""
    mission_game.add_mission("trade_proposal")
    [mission] = mission_game.state.missions
    mission.demand = 9_999  # impossible
    mission.demand_type = "energy"  # player has none
    mission.deadline = datetime.datetime.now() - datetime.timedelta(seconds=1)

    clay_before = mission_game.resources.get("clay")
    mission_game.complete_missions()

    assert mission_game.state.missions == []
    # Failure does not pay the reward and does not consume resources.
    assert mission_game.resources.get("clay") == clay_before


def test_unmet_mission_stays_in_state(mission_game, auto_accept):
    """Insufficient resources + active deadline → mission lingers."""
    mission_game.add_mission("trade_proposal")
    [mission] = mission_game.state.missions
    mission.demand = 9_999
    mission.demand_type = "energy"
    mission.deadline = datetime.datetime.now() + datetime.timedelta(hours=1)

    mission_game.complete_missions()
    assert len(mission_game.state.missions) == 1


def test_mission_persists_through_save_load(mission_game, auto_accept, tmp_path):
    """Accepted missions survive a save/load round-trip."""
    from shellcraft.shellcraft import Game

    mission_game.add_mission("trade_proposal")
    save_path = mission_game.save_file
    mission_game.save()

    reloaded = Game.load(save_path)
    assert len(reloaded.state.missions) == 1
    revived = reloaded.state.missions[0]
    assert revived.name == "trade_proposal"
    assert revived.deadline is not None
    # Template lookup still works on the reloaded instance.
    assert "ask" in revived.template.strings
