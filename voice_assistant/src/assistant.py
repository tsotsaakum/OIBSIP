"""Lentswe chat loop: persona + JSON memory + Groq tool calls (Aria-style, not Claude)."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

from src import store
from src.geo import driving_summary
from src.mail import send_email
from src.languages import SOUTH_AFRICAN_LANGUAGES
from src.memory import lasting_notes
from src.tools import emergency_info
from src.weather import forecast_place

load_dotenv(override=True)

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Live Open-Meteo weather. Never invent °C. Pass a town. If the user said “here/home” you may use their profile city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Town, e.g. Durban"},
                    "tomorrow": {"type": "boolean", "description": "True for tomorrow’s forecast"},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_directions",
            "description": "Driving summary via OpenRouteService. Needs ORS_API_KEY. Ask if origin or destination is missing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["origin", "destination"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Save a to-do in lasting JSON memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "due_date": {"type": "string"},
                    "priority": {"type": "string"},
                },
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark an open task done by matching its text.",
            "parameters": {
                "type": "object",
                "properties": {"description": {"type": "string"}},
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List open tasks from JSON memory.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_goal",
            "description": "Save a structured goal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "target": {"type": "number"},
                    "deadline": {"type": "string"},
                },
                "required": ["goal"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_goals",
            "description": "List stored goals.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_symptom",
            "description": "Append a symptom diary entry. Not a diagnosis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symptom": {"type": "string"},
                    "severity": {"type": "string"},
                },
                "required": ["symptom"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_symptoms",
            "description": "Show recent symptom log.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_profile_fact",
            "description": "Remember a profile fact (name, home city, preferred language).",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_emergency_info",
            "description": "SA emergency numbers. Use for hurt, fire, danger. You cannot call or SMS.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Timed reminder stored in JSON. The browser page must stay open to speak it when due.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "seconds": {"type": "integer", "description": "Delay in seconds from now"},
                },
                "required": ["text", "seconds"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send a test email via SMTP. Needs SMTP_HOST, SMTP_USER, SMTP_PASSWORD. Never claim it was sent if those are empty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_addr": {"type": "string"},
                    "body": {"type": "string"},
                    "subject": {"type": "string"},
                },
                "required": ["to_addr", "body"],
            },
        },
    },
]


def build_system_prompt(language_name: str) -> str:
    return f"""You are Lentswe, not Aria, not Alexa.

<persona>
Warm, brief South African voice. 2–4 spoken sentences. Light SA English only when the reply language is English. Clean grammar in {language_name}. Never claim you sent SMS, called police, or booked travel.
</persona>

<scope>
You help with: conversation, live weather (tool only), tasks/goals/symptoms/profile in JSON memory, SA emergency numbers, travel talk, pointing people to the Home tab for maps.
You do not: diagnose, prescribe, clone voices, pirate music, smart-home control, or invent °C.
Always reply in {language_name} only unless they asked to switch.
</scope>

<ambiguity>
If a town, origin, or destination is missing, ask — do not guess Johannesburg. If it is unclear whether they mean a task or a goal, ask one short question.
</ambiguity>

<cross_domain_reasoning>
Weigh weather + goals + health + open tasks together when the user asks something like “should I go for a run today” or “what to pack for Durban”. Use tool results and LASTING MEMORY only. Packing and trip questions must call get_weather for that city — never a year-round climate cliché. Do not invent numbers.
</cross_domain_reasoning>

<lasting_memory>
{lasting_notes()}
</lasting_memory>
"""


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    args = arguments or {}
    if name == "get_weather":
        loc = str(args.get("location") or "").strip()
        if not loc or loc.lower() in {"here", "home", "nearby"}:
            profile = store.profile()
            loc = str(
                profile.get("city")
                or profile.get("home_city")
                or profile.get("town")
                or loc
            ).strip()
        if not loc or loc.lower() in {"here", "home", "nearby"}:
            return "Need a town name (or save a city on the profile). Ask the user — do not guess Johannesburg."
        return forecast_place(loc, tomorrow=bool(args.get("tomorrow")))
    if name == "get_directions":
        return driving_summary(str(args.get("origin") or ""), str(args.get("destination") or ""))
    if name == "add_task":
        item = store.add_task(
            str(args.get("description") or ""),
            due_date=args.get("due_date") or None,
            priority=str(args.get("priority") or "normal"),
        )
        return f"Saved task: {item['description']}"
    if name == "complete_task":
        item = store.complete_task(str(args.get("description") or ""))
        return f"Marked done: {item['description']}" if item else "No matching open task."
    if name == "list_tasks":
        open_ = store.open_tasks()
        return "Open tasks: " + "; ".join(t["description"] for t in open_) if open_ else "No open tasks."
    if name == "add_goal":
        target = args.get("target")
        try:
            target_f = float(target) if target is not None else None
        except (TypeError, ValueError):
            target_f = None
        item = store.add_goal(str(args.get("goal") or ""), target=target_f, deadline=args.get("deadline") or None)
        return f"Saved goal: {item['goal']}"
    if name == "list_goals":
        items = store.goals()
        return "Goals: " + "; ".join(g["goal"] for g in items) if items else "No goals stored."
    if name == "log_symptom":
        item = store.add_symptom(str(args.get("symptom") or ""), severity=args.get("severity") or None)
        return f"Logged symptom: {item['symptom']}. Not a diagnosis."
    if name == "list_symptoms":
        rows = store.symptoms()
        return "Symptoms: " + "; ".join(r["symptom"] for r in rows) if rows else "No symptoms logged."
    if name == "set_profile_fact":
        store.set_profile(str(args.get("key") or "note"), str(args.get("value") or ""))
        return "Profile updated."
    if name == "get_emergency_info":
        return emergency_info()
    if name == "set_reminder":
        try:
            seconds = int(args.get("seconds") or 0)
        except (TypeError, ValueError):
            seconds = 0
        text = str(args.get("text") or "").strip()
        if seconds <= 0 or not text:
            return "Need reminder text and a positive delay in seconds."
        item = store.add_reminder(text, seconds)
        return (
            f"Reminder set for {seconds} seconds: {item['text']}. "
            "Keep the Lentswe page open so it can speak when due."
        )
    if name == "send_email":
        return send_email(
            str(args.get("to_addr") or ""),
            str(args.get("body") or ""),
            str(args.get("subject") or "Message from Lentswe"),
        )
    return f"Unknown tool: {name}"


def chat_turn(user_text: str, language_id: str, history: list[dict], api_key: str) -> str:
    from openai import OpenAI

    language_name = SOUTH_AFRICAN_LANGUAGES.get(language_id, SOUTH_AFRICAN_LANGUAGES["english"]).name
    from src.chat import chat_model

    client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None)
    model = chat_model()
    messages: list[dict] = [{"role": "system", "content": build_system_prompt(language_name)}]
    for turn in history[-16:]:
        role = turn.get("role")
        content = turn.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_text})

    for _ in range(6):
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": 0.5,
            "max_completion_tokens": 2048,
            "extra_body": {"include_reasoning": False},
        }
        used_tools = any(m.get("role") == "tool" for m in messages)
        try:
            if used_tools:
                result = client.chat.completions.create(
                    **kwargs, tools=TOOL_DEFINITIONS, tool_choice="auto"
                )
            else:
                try:
                    result = client.chat.completions.create(
                        **kwargs, tools=TOOL_DEFINITIONS, tool_choice="auto"
                    )
                except Exception:
                    plain = dict(kwargs)
                    plain.pop("extra_body", None)
                    result = client.chat.completions.create(**plain)
        except Exception:
            return (
                "I could not finish that Groq reply. "
                "Ask again with a town name, for example: should I run in Durban today?"
            )
        choice = result.choices[0]
        msg = choice.message
        calls = getattr(msg, "tool_calls", None) or []
        if not calls:
            text = (msg.content or "").strip()
            if not text or text.lower() == user_text.strip().lower():
                return (
                    "I did not get a real answer from chat. "
                    "Try: should I go for a run in Durban today?"
                )
            return text
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {
                            "name": c.function.name,
                            "arguments": c.function.arguments or "{}",
                        },
                    }
                    for c in calls
                ],
            }
        )
        for call in calls:
            raw = call.function.arguments or "{}"
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {}
            output = execute_tool(call.function.name, parsed if isinstance(parsed, dict) else {})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": output,
                }
            )
    return "I hit the tool-call limit. Ask again in a shorter sentence."


def main() -> None:
    load_dotenv(override=True)
    key = (os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or "").strip()
    if not key:
        print("Set OPENAI_API_KEY (Groq) in .env, then run: python -m src.assistant")
        return
    history: list[dict] = []
    print("Lentswe — type in this window. Voice still lives in the web app (python app.py).")
    print("Quit with Ctrl+C or the word quit.")
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not user:
            continue
        if user.lower() in {"quit", "exit"}:
            return
        reply = chat_turn(user, "english", history, key)
        print("Lentswe:", reply)
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
