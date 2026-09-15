"""Desktop text loop. The website still runs from app.py."""

from __future__ import annotations

import sys
from pathlib import Path

# Folder that contains "src" (voice-assistant), so "import src" works
# even if you run: python src/main.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.brain import think
from src.wake_word import is_wake, strip_wake


def handle_utterance(
    text: str,
    language_id: str = "english",
    history: list[dict] | None = None,
) -> str | None:
    """Return a reply only if the line contains a wake word. Otherwise None."""
    history = history or []
    if not is_wake(text):
        return None
    leftover = strip_wake(text)
    if not leftover:
        return think("hello", language_id, history)
    return think(leftover, language_id, history)


def run() -> None:
    print("Lentswe desktop loop. Start a line with Lentswe. Type quit to exit.")
    print("Example: Lentswe, the date")
    history: list[dict] = []
    while True:
        text = input("> ").strip()
        if not text:
            continue
        if text.lower() in {"quit", "exit"}:
            print("Bye.")
            break
        answer = handle_utterance(text, history=history)
        if answer is None:
            print("(Say Lentswe first.)")
            continue
        print(answer)
        leftover = strip_wake(text) or text
        history.append({"role": "user", "content": leftover})
        history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    run()
