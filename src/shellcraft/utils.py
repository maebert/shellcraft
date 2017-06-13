# coding=utf-8

"""Utility methods."""

from __future__ import absolute_import, division, print_function, unicode_literals
from random import random

import datetime

__author__ = "Manuel Ebert"
__email__ = "manuel@1450.me"


RESOURCE_WORTH = {
    'clay': 1,
    'ore': 2,
    'energy': 4
}


def to_date(delta_seconds=0):
    """Convert delta in seconds to ISO-8601 string."""
    return (datetime.datetime.now() + datetime.timedelta(seconds=delta_seconds)).isoformat()


def parse_isoformat(s):
    """Parse ISO-8601 string."""
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")


def convert_resource_value(frm, to):
    """Return the market value of a resource to trade."""
    return 1.0 * RESOURCE_WORTH[frm] / RESOURCE_WORTH[to]


def to_list(string_or_list):
    """Encapsulate strings or numbers in a list."""
    if not string_or_list:
        return []
    if not isinstance(string_or_list, (list, tuple)):
        return [string_or_list]
    return string_or_list


def to_float(s):
    """Convert anything to float.

    Examples:
        >>> to_float('.4')
        .4
        >>> to_float('random(1, 9)')
        6
    """
    if s.startswith("random"):
        low, high = map(float, s[6:].strip("()").split(","))
        return low + random() * (high - low)
    return float(s)


def format_name(npc):
    """Generate the display name of an NPC."""
    if not npc or not npc.display:
        return "Anonymous"
    return npc.display.format(
        first=npc.first,
        middle=npc.middle,
        last=npc.last,
        title=npc.title,
        nickname=npc.nickname,
        first_initial=npc.first[0] + ".",
        middle_initial=npc.middle[0] + "."
    ).strip()
