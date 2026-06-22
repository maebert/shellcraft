"""Faction seeding helpers."""

import os

import toml

from shellcraft.game_state import Fraction

FIXTURES = "fractions.toml"


def seed_defaults(fractions: list) -> None:
    """Append any factions from the fixture file that aren't already present."""
    by_name = {f.name for f in fractions}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", FIXTURES)
    data = toml.load(path)
    for name, payload in data.items():
        if name not in by_name:
            fractions.append(Fraction(name=name, influence=payload["influence"]))
