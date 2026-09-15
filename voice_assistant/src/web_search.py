"""Web search skill — placeholder until we add a search API together."""

import httpx

HEADERS = {
    "User-Agent": "LentsweVoiceAssistant/1.0 (local educational project)",
    "Accept": "application/json",
}


def search(query: str) -> str:
    try:
        with httpx.Client(timeout=15.0, headers=HEADERS) as client:
            data = client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                      "format": "json",
                        "list": "search", 
                        "srsearch": query,
                        "srlimit" : 1,
                        "format": "json",
                        "utf8": 1,

                        },
            ).json()
            hits = (data.get("query") or {}).get("search") or []
            if not hits:
                return f"I  couldn't find a page for {query}."
            title = hits[0]["title"]
            slug = title.replace(" ","_")
            page = client.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"   
            )

            page.raise_for_status()
            extract = (page.json().get("extract") or "").strip()
            if not extract:
                return f"I found {title}, but there was no summary ."
            return extract
    except httpx.HTTPError:
        return "Search is down right now. Try again in a minute. "
    