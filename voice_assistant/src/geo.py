"""OpenStreetMap Nominatim for a home pin. Not a Google Maps clone."""

from __future__ import annotations

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

HEADERS = {"User-Agent": "LentsweVoiceAssistant/1.0 (student portfolio)"}


def geocode_place(query: str) -> dict | None:
    q = (query or "").strip()
    if not q or len(q) > 200:
        return None
    params = {"q": q, "format": "json", "limit": 1}
    with httpx.Client(timeout=15.0, headers=HEADERS) as client:
        rows = client.get("https://nominatim.openstreetmap.org/search", params=params).json()
    if not rows:
        return None
    row = rows[0]
    lat = float(row["lat"])
    lon = float(row["lon"])
    pad = 0.02
    bbox = f"{lon - pad},{lat - pad},{lon + pad},{lat + pad}"
    embed = (
        "https://www.openstreetmap.org/export/embed.html?"
        f"bbox={bbox}&layer=mapnik&marker={lat}%2C{lon}"
    )
    return {
        "lat": lat,
        "lon": lon,
        "label": row.get("display_name") or q,
        "embed": embed,
    }


def driving_summary(origin: str, destination: str) -> str:
    origin = (origin or "").strip()
    destination = (destination or "").strip()
    if not origin or not destination:
        return "Need both origin and destination. Ask — do not guess."
    key = os.getenv("ORS_API_KEY", "").strip()
    if not key:
        return (
            "Driving directions need a free OpenRouteService key. "
            "Add ORS_API_KEY in .env (openrouteservice.org). "
            "Until then use the Home tab: Guide me home."
        )
    start = geocode_place(origin)
    end = geocode_place(destination)
    if not start or not end:
        return "I could not pin origin or destination on OpenStreetMap. Try fuller place names."
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {**HEADERS, "Authorization": key, "Content-Type": "application/json"}
    payload = {
        "coordinates": [
            [start["lon"], start["lat"]],
            [end["lon"], end["lat"]],
        ]
    }
    with httpx.Client(timeout=20.0, headers=headers) as client:
        res = client.post(url, json=payload)
    if res.status_code != 200:
        return "OpenRouteService refused that route. Try different place names, or use Guide me home."
    body = res.json()
    try:
        if "features" in body:
            summary = body["features"][0]["properties"]["summary"]
        else:
            summary = body["routes"][0]["summary"]
        km = float(summary["distance"]) / 1000
        minutes = float(summary["duration"]) / 60
    except (KeyError, IndexError, TypeError, ValueError):
        return "The directions feed came back in a shape I do not read. I will not invent a route."
    return (
        f"OpenRouteService drive: {start['label']} to {end['label']}. "
        f"About {km:.1f} km, {minutes:.0f} minutes. "
        "This is a live route summary, not turn-by-turn inside Lentswe."
    )
