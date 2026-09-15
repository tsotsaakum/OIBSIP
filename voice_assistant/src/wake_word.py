"""Wake phrase. Mic is click-to-talk — we do not listen in the background."""

from __future__ import annotations

import re

WAKE_WORDS = ("hey lentswe", "hello lentswe", "lentswe")


def is_wake(text: str) -> bool:
    lowered = (text or "").lower().strip()
    return any(word in lowered for word in WAKE_WORDS)


def is_wake_only(text: str) -> bool:
    cleaned = re.sub(r"[^\w\s]", " ", (text or "").lower())
    cleaned = " ".join(cleaned.split())
    return cleaned in WAKE_WORDS


def strip_wake(text: str) -> str:
    leftover = (text or "").strip()
    lowered = leftover.lower()
    for word in sorted(WAKE_WORDS, key=len, reverse=True):
        index = lowered.find(word)
        if index != -1:
            leftover = leftover[:index] + leftover[index + len(word) :]
            return leftover.strip(" ,.")
    return leftover


def wake_greeting() -> str:
    return "Yes, I'm Lentswe. What do you need?"
