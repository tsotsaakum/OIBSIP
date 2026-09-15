"""JSON memory on disk so tasks, goals, and symptoms survive a restart."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def data_path() -> Path:
    override = (os.getenv("LENTSWE_DATA_DIR") or "").strip()
    if override:
        return Path(override) / "lentswe.json"
    return ROOT / "data" / "lentswe.json"


def _empty() -> dict:
    return {"tasks": [], "goals": [], "symptoms": [], "profile": {}, "reminders": []}


def load() -> dict:
    path = data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return _empty()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _empty()
    for key, default in (("tasks", []), ("goals", []), ("symptoms", []), ("profile", {}), ("reminders", [])):
        data.setdefault(key, default)
    if not isinstance(data.get("profile"), dict):
        data["profile"] = {}
    return data


def save(data: dict) -> None:
    path = data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def add_task(description: str, due_date: str | None = None, priority: str = "normal") -> dict:
    data = load()
    item = {
        "id": uuid.uuid4().hex[:8],
        "description": description.strip(),
        "due_date": due_date,
        "done": False,
        "priority": priority,
    }
    data["tasks"].append(item)
    save(data)
    return item


def complete_task(needle: str) -> dict | None:
    data = load()
    needle = needle.strip().lower()
    for item in data["tasks"]:
        if not item.get("done") and needle in (item.get("description") or "").lower():
            item["done"] = True
            save(data)
            return item
    return None


def open_tasks() -> list[dict]:
    return [t for t in load()["tasks"] if not t.get("done")]


def add_goal(goal: str, target: float | None = None, deadline: str | None = None) -> dict:
    data = load()
    item = {
        "id": uuid.uuid4().hex[:8],
        "goal": goal.strip(),
        "target": target,
        "deadline": deadline,
        "progress": 0,
    }
    data["goals"].append(item)
    save(data)
    return item


def goals() -> list[dict]:
    return load()["goals"]


def add_symptom(symptom: str, severity: str | None = None) -> dict:
    data = load()
    item = {
        "id": uuid.uuid4().hex[:8],
        "symptom": symptom.strip(),
        "severity": severity,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    data["symptoms"].append(item)
    save(data)
    return item


def symptoms() -> list[dict]:
    return load()["symptoms"][-20:]


def set_profile(key: str, value: str) -> dict:
    data = load()
    data.setdefault("profile", {})
    data["profile"][key.strip()] = value.strip()
    save(data)
    return data["profile"]


def profile() -> dict:
    data = load()
    raw = data.get("profile") or {}
    return raw if isinstance(raw, dict) else {}

def add_reminder(text: str, seconds: int) -> dict:
    from datetime import timedelta

    data = load()
    due = datetime.now(timezone.utc) + timedelta(seconds=max(1, int(seconds)))
    item = {
        "id": uuid.uuid4().hex[:8],
        "text": text.strip(),
        "due_at": due.isoformat(timespec="seconds"),
        "done": False,
        "spoken": False,
    }
    data.setdefault("reminders", []).append(item)
    save(data)
    return item


def due_reminders() -> list[dict]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out = []
    data = load()
    changed = False
    for item in data.get("reminders") or []:
        if item.get("done") or item.get("spoken"):
            continue
        if (item.get("due_at") or "") <= now:
            item["spoken"] = True
            changed = True
            out.append(item)
    if changed:
        save(data)
    return out