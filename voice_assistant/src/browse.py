"""Open a web search in the system browser (assignment: webbrowser)."""

from __future__ import annotations

import re
import urllib.parse
import webbrowser


def open_web_search(user_text: str) -> str:
    text = (user_text or "").strip()
    query = re.sub(
        r"^(please\s+)?(search(\s+the\s+web)?(\s+for)?|google|look\s+up|batla|funa)\s+",
        "",
        text,
        flags=re.I,
    ).strip(" ?.")
    if not query or query.lower() == text.lower():
        query = text
    if not query:
        return "Say what to search, for example: search for Table Mountain."
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    return f"I opened a browser search for {query}."
