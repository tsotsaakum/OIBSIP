"""Concrete tools with clear inputs — not one fuzzy Safety/Health/Goals blob."""

from __future__ import annotations

import re

from src.mail import try_send_email
from src import store

EMERGENCY = (
    "call for help",
    "i'm hurt",
    "im hurt",
    "i am hurt",
    "there's a fire",
    "there is a fire",
    "emergency",
    "police",
    "ambulance",
    "10111",
    "10177",
    "not safe",
    "in danger",
    "i'm in danger",
    "i am in danger",
)


def run_tool(user_text: str) -> str | None:
    text = (user_text or "").strip()
    if not text:
        return None
    lower = text.lower()

    if any(p in lower for p in EMERGENCY):
        return emergency_info()

    hit = _log_symptom(text, lower)
    if hit:
        return hit
    if any(p in lower for p in ("my symptoms", "symptom log", "show symptoms")):
        return list_symptoms()

    hit = _complete_task(text, lower)
    if hit:
        return hit
    hit = _add_task(text, lower)
    if hit:
        return hit
    if any(
        p in lower
        for p in ("what's on my list", "what is on my list", "show my tasks", "my tasks", "my list")
    ):
        return list_tasks()
    if "what should i do first" in lower or "priorit" in lower:
        return prioritize_tasks()

    if any(p in lower for p in ("how am i doing", "my goals", "show my goals", "what are my goals")):
        return list_goals()
    hit = _add_goal(text, lower)
    if hit:
        return hit

    mailed = try_send_email(text)
    if mailed:
        return mailed

    return None


def emergency_info() -> str:
    return (
        "If this is an emergency, call now — I cannot send police or share your GPS. "
        "South Africa: 112 (cellphone emergency), 10111 (police), 10177 (ambulance). "
        "Share your live location with a person you trust, not with this app. "
        "I do not send SMS for you."
    )


def _add_task(text: str, lower: str) -> str | None:
    match = re.match(
        r"^(?:add to (?:my )?(?:list|todo)|add task|remind me to)\s+(.+)$",
        text,
        re.I,
    )
    if not match:
        return None
    item = store.add_task(match.group(1).strip())
    return f"Task saved: {item['description']}. Say “what’s on my list” or “mark {item['description']} as done”."


def _complete_task(text: str, lower: str) -> str | None:
    match = re.match(r"^(?:mark|tick|complete|done)\s+(.+?)\s+(?:as )?done$", text, re.I)
    if not match:
        match = re.match(r"^i (?:did|finished|done)\s+(.+)$", text, re.I)
    if not match:
        return None
    item = store.complete_task(match.group(1))
    if not item:
        return "I could not find that open task. Say “what’s on my list”."
    return f"Marked done: {item['description']}."


def list_tasks() -> str:
    open_ = store.open_tasks()
    if not open_:
        return "Your task list is empty. Say “add to my list buy bread”."
    lines = [t["description"] for t in open_]
    return "Open tasks: " + "; ".join(lines) + "."


def prioritize_tasks() -> str:
    open_ = store.open_tasks()
    if not open_:
        return "No open tasks to rank. Add one first."
    first = open_[0]["description"]
    rest = [t["description"] for t in open_[1:3]]
    extra = (" Then: " + "; ".join(rest) + ".") if rest else ""
    return (
        f"I am not a manager — I only stored the list. Start with: {first}.{extra} "
        "Mark one done when you finish it."
    )


def _add_goal(text: str, lower: str) -> str | None:
    match = re.match(r"^(?:my goal is|add goal|new goal)\s+(.+)$", text, re.I)
    if not match:
        match = re.match(r"^i want to\s+((?:save|run)\b.+)$", text, re.I)
    if not match:
        return None
    raw = match.group(1).strip()
    target = None
    money = re.search(r"(?:r|\$)\s*(\d+(?:\.\d+)?)", raw, re.I)
    if money:
        target = float(money.group(1))
    else:
        num = re.search(r"\b(\d+(?:\.\d+)?)\b", raw)
        if num and any(w in raw.lower() for w in ("save", "rands", "rand", "$")):
            target = float(num.group(1))
    deadline = None
    if "this month" in lower or "end of the month" in lower:
        deadline = "end of this month"
    item = store.add_goal(raw, target=target, deadline=deadline)
    bits = [item["goal"]]
    if item["target"] is not None:
        bits.append(f"target {item['target']:g}")
    if item["deadline"]:
        bits.append(item["deadline"])
    return "Goal saved: " + ", ".join(bits) + ". Say “how am I doing on my goals”."


def list_goals() -> str:
    items = store.goals()
    if not items:
        return "No goals stored yet. Say “my goal is save 500 this month”."
    parts = []
    for g in items[-5:]:
        line = g["goal"]
        if g.get("target") is not None:
            line += f" (target {g['target']:g}, progress {g.get('progress') or 0})"
        parts.append(line)
    return "Your goals: " + "; ".join(parts) + "."


def _log_symptom(text: str, lower: str) -> str | None:
    match = re.match(
        r"^(?:log (?:that i have |a |an )?|log symptom |i have (?:a |an )?)",
        text,
        re.I,
    )
    if "log" not in lower:
        return None
    body = re.sub(
        r"^(?:log (?:that i have |a |an )?|log symptom |i have (?:a |an )?)",
        "",
        text,
        flags=re.I,
    ).strip(" .")
    if not body:
        return None
    sev = None
    for word in ("mild", "moderate", "severe"):
        if word in lower:
            sev = word
    item = store.add_symptom(body, severity=sev)
    return (
        f"Logged symptom: {item['symptom']}. This is a personal log, not a diagnosis. "
        "If you feel worse, call 112 or a clinician. Say “show my symptoms” to hear recent entries."
    )


def list_symptoms() -> str:
    rows = store.symptoms()
    if not rows:
        return "No symptoms logged. Say “log that I have a headache”."
    parts = [r["symptom"] for r in rows[-8:]]
    return (
        "Recent symptom log: "
        + "; ".join(parts)
        + ". I am not a doctor and I will not diagnose this."
    )
