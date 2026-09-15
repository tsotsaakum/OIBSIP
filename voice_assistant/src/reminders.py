"""Timed reminders stored in JSON. The browser polls /api/reminders/due and speaks them."""

from __future__ import annotations

import re

from src import store


def try_set_reminder(user_text: str) -> str | None:
    match = re.search(
        r"remind me in (\d+)\s*(seconds?|minutes?|mins?|hours?|hrs?)\s+(?:to\s+)?(.+)",
        user_text or "",
        re.I,
    )
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2).lower()
    what = match.group(3).strip(" .")
    if not what:
        return "Say what to remind you, for example: remind me in 1 minute to drink water."
    if unit.startswith("second"):
        seconds = amount
    elif unit.startswith("hour") or unit.startswith("hr"):
        seconds = amount * 3600
    else:
        seconds = amount * 60
    item = store.add_reminder(what, seconds)
    return (
        f"Reminder set for {amount} {match.group(2)}: {item['text']}. "
        "Keep this page open so I can speak it when the time is up."
    )
