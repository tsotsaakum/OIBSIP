"""User-defined phrases from config/commands.json."""

from __future__ import annotations

import json
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "commands.json"


def try_custom_command(user_text: str) -> str | None:
    text = (user_text or "").strip().lower()
    if not text or not CONFIG.exists():
        return None
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    spec = data.get(text)
    if not isinstance(spec, dict):
        for phrase, row in data.items():
            if isinstance(phrase, str) and phrase.lower() in text and isinstance(row, dict):
                spec = row
                break
        else:
            return None
    action = (spec.get("action") or "").strip()
    if action == "open_url":
        url = (spec.get("url") or "").strip()
        if not url:
            return None
        webbrowser.open(url)
        return f"I opened {url}."
    if action == "say":
        line = (spec.get("text") or "").strip()
        return line or None
    return None
