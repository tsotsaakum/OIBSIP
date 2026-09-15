"""System facts: time, and later: volume, stop listening."""

from datetime import datetime


def current_time() -> str:
    return datetime.now().strftime("%H:%M")


def status_line() -> str:
    return f"Lentswe is running. Local time is {current_time()}."


def current_date() -> str:
    return datetime.now().strftime("%A, %d %B %Y")


def stop_reply() -> str:
    return "Okay. I'll wait. Say Lentswe when you want me again."


def volume_reply(user_text: str) -> str:
    text = user_text.lower()
    if any(word in text for word in ("up", "louder", "increase", "phahamisa")):
        return (
            "I can't move Windows volume from the website yet. "
            "Use the speaker keys on your keyboard."
        )
    if any(word in text for word in ("down", "quieter", "decrease", "mute", "thoba")):
        return (
            "I can't move Windows volume from the website yet. "
            "Use the speaker keys on your keyboard."
        )
    return "Say volume up or volume down. I can't turn the PC speakers from this file yet."