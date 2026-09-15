"""Session chat plus lasting notes from the JSON store."""

from __future__ import annotations

from src import store


class Memory:
    def __init__(self, limit: int = 16):
        self.limit = limit
        self.turns: list[dict] = []

    def add(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content})
        self.turns = self.turns[-self.limit :]

    def history(self) -> list[dict]:
        return list(self.turns)

    def clear(self) -> None:
        self.turns = []

    def last(self) -> dict | None:
        if not self.turns:
            return None
        return self.turns[-1]


def lasting_notes() -> str:
    """Facts Lentswe may use. Not invented. Empty lines if the user stored nothing."""
    data = store.load()
    tasks = [t["description"] for t in data.get("tasks") or [] if not t.get("done")]
    goals = []
    for g in data.get("goals") or []:
        bit = g.get("goal") or ""
        if g.get("target") is not None:
            bit += f" (target {g['target']}, progress {g.get('progress') or 0})"
        if bit:
            goals.append(bit)
    symptoms = [s.get("symptom") or "" for s in (data.get("symptoms") or [])[-8:]]
    symptoms = [s for s in symptoms if s]
    profile = store.profile()
    facts = [f"{k}: {v}" for k, v in profile.items() if v]
    lines = [
        "Profile: " + ("; ".join(facts) if facts else "none"),
        "Open tasks: " + ("; ".join(tasks) if tasks else "none"),
        "Goals: " + ("; ".join(goals) if goals else "none"),
        "Recent symptom log: " + ("; ".join(symptoms) if symptoms else "none"),
    ]
    return "\n".join(lines)
