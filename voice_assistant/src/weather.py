"""Live weather via Open-Meteo only. Never invent numbers."""

from __future__ import annotations

import re

import httpx

ALIASES = {
    "joburg": "Johannesburg",
    "jozi": "Johannesburg",
    "jhb": "Johannesburg",
    "egoli": "Johannesburg",
    "soweto": "Soweto",
    "sandton": "Sandton",
    "tshwane": "Pretoria",
    "pta": "Pretoria",
    "cape town": "Cape Town",
    "kaapstad": "Cape Town",
    "kaap": "Cape Town",
    "ekapa": "Cape Town",
    "durban": "Durban",
    "ethekwini": "Durban",
    "dbn": "Durban",
    "johannesburg": "Johannesburg",
    "pretoria": "Pretoria",
    "mangaung": "Bloemfontein",
    "bloem": "Bloemfontein",
    "gqeberha": "Gqeberha",
    "port elizabeth": "Gqeberha",
    "east london": "East London",
    "e monti": "East London",
    "pietersburg": "Polokwane",
    "polokwane": "Polokwane",
    "nelspruit": "Mbombela",
    "mbombela": "Mbombela",
    "mafikeng": "Mahikeng",
    "mahikeng": "Mahikeng",
    "kimberley": "Kimberley",
    "upington": "Upington",
    "george": "George",
    "stellenbosch": "Stellenbosch",
    "emalahleni": "eMalahleni",
    "witbank": "eMalahleni",
}

WMO = {
    0: "clear skies",
    1: "mainly clear skies",
    2: "partly cloudy skies",
    3: "overcast skies",
    45: "fog",
    48: "freezing fog",
    51: "light drizzle",
    53: "drizzle",
    55: "heavy drizzle",
    56: "freezing drizzle",
    57: "heavy freezing drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    66: "freezing rain",
    67: "heavy freezing rain",
    71: "light snow",
    73: "snow",
    75: "heavy snow",
    77: "snow grains",
    80: "light rain showers",
    81: "rain showers",
    82: "heavy rain showers",
    85: "light snow showers",
    86: "heavy snow showers",
    95: "thunderstorms",
    96: "thunderstorms with hail",
    99: "severe thunderstorms with hail",
}

WEATHER_WORDS = (
    "weather",
    "forecast",
    "temperature",
    "how hot",
    "how cold",
    "raining",
    "rainy",
    "storm",
    "humidity",
    "windy",
    "weer",
    "imozulu",
    "isimo sezulu",
    "sezulu",
    "imvula",
    "mvula",
    "bosa",
    "lehodimo",
    "leholimo",
    "isirimo",
    "maxelo",
    "mpfula",
    "tshifhefho",
    "pula",
)


def is_weather_query(user_text: str) -> bool:
    text = (user_text or "").lower()
    return any(word in text for word in WEATHER_WORDS)


def is_pack_query(user_text: str) -> bool:
    text = (user_text or "").lower()
    pack = any(
        w in text
        for w in (
            "what to pack",
            "what should i pack",
            "pack for",
            "packing for",
            "packing list",
            "what do i pack",
        )
    )
    trip = any(w in text for w in ("trip", "holiday", "vacation", "weekend away"))
    return pack or (trip and bool(_place_from(user_text)))


COASTAL = {
    "Durban",
    "Cape Town",
    "Gqeberha",
    "East London",
    "George",
}

RAIN_CODES = {
    51,
    53,
    55,
    56,
    57,
    61,
    63,
    65,
    66,
    67,
    80,
    81,
    82,
    95,
    96,
    99,
}


def pack_for_trip(user_text: str) -> str:
    """Live Open-Meteo packing list. No climate clichés, no invented °C."""
    place = _place_from(user_text)
    if not place:
        return (
            "Name the city you are packing for, for example: "
            "what to pack for Durban, or what to pack for Cape Town."
        )
    try:
        geo = _geocode(place)
        if not geo:
            return (
                f"I could not find {place} in the weather atlas. "
                "Use a South African town name."
            )
        name, lat, lon, country = geo
        current = _current(lat, lon)
        daily = _daily(lat, lon)
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return "The live weather feed is down. I will not invent a packing list. Try again in a minute."

    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    code = int(current.get("weather_code") or 0)
    if temp is None:
        return f"Open-Meteo found {place} but sent no temperature. I will not guess what to pack."

    tmax = (daily.get("temperature_2m_max") or [None])[0]
    tmin = (daily.get("temperature_2m_min") or [None])[0]
    day_code = int((daily.get("weather_code") or [code])[0] or code)
    sky = WMO.get(code, "conditions not listed in the weather code table")
    where = name if country == "South Africa" else f"{name}, {country}"

    bag: list[str] = []
    hot = temp >= 24 or (tmax is not None and tmax >= 24)
    cool = temp <= 16 or (tmin is not None and tmin <= 16)
    if hot:
        bag.append("light clothes, a hat, and sunscreen")
    if cool:
        bag.append("a warm layer for morning or evening")
    if not hot and not cool:
        bag.append("a mix of light clothes and one warmer layer")
    humidity = 0 if humidity is None else humidity
    wind = 0 if wind is None else wind
    if humidity >= 65:
        bag.append("breathable fabrics — it is humid on the feed, not a year-round guess")
    if code in RAIN_CODES or day_code in RAIN_CODES:
        bag.append("a compact rain jacket")
    if wind >= 25:
        bag.append("a windbreaker")
    if name in COASTAL:
        bag.append("swimwear if you swim, and only at guarded beaches")

    from src import store

    related = []
    needle = name.lower()
    for task in store.open_tasks():
        desc = (task.get("description") or "").strip()
        low = desc.lower()
        if "pack" in low or needle in low:
            related.append(desc)

    bits = [
        f"Live Open-Meteo for {where}: {temp:.0f}°C, {sky}, humidity {humidity:.0f}%, wind {wind:.0f} km/h."
    ]
    if tmax is not None and tmin is not None:
        bits.append(f"Today’s forecast band: {tmin:.0f}–{tmax:.0f}°C.")
    bits.append("Pack: " + "; ".join(bag) + ".")
    if related:
        bits.append("On your list: " + "; ".join(related) + ".")
    bits.append("I do not book tickets. This list follows the live feed, not a brochure.")
    return " ".join(bits)


def is_run_query(user_text: str) -> bool:
    text = (user_text or "").lower()
    if "run" not in text and "jog" not in text:
        return False
    return any(
        w in text
        for w in ("should i", "can i", "today", "this morning", "this evening", "go for")
    )


def _place_from_memory() -> str | None:
    from src import store

    bits = [t.get("description") or "" for t in store.open_tasks()]
    bits += [g.get("goal") or "" for g in store.goals()]
    bits += [f"{k} {v}" for k, v in store.profile().items()]
    return _place_from(" ".join(bits))


def run_today_reply(user_text: str) -> str:
    """Live weather + goals + symptom log. Not a coaching echo of the question."""
    from src import store

    place = _place_from(user_text) or _place_from_memory()
    if not place:
        return (
            "I will not guess where you run. Name the town, for example: "
            "should I go for a run in Durban today?"
        )
    weather = forecast_place(place)
    if weather.startswith("I will not") or weather.startswith("I could not") or "feed is down" in weather:
        return weather

    run_goals = [
        g.get("goal") or ""
        for g in store.goals()
        if any(w in (g.get("goal") or "").lower() for w in ("run", "jog", "fitness", "walk"))
    ]
    symptoms = [s.get("symptom") or "" for s in store.symptoms()[-5:] if s.get("symptom")]
    bits = [weather]
    if run_goals:
        bits.append("Your run-related goal: " + "; ".join(run_goals) + ".")
    if symptoms:
        bits.append(
            "Recent symptom log: "
            + "; ".join(symptoms)
            + ". That is a diary, not a diagnosis — skip the run if you feel worse, or call 112."
        )
    else:
        bits.append("No recent symptom log stored.")
    bits.append(
        "I am not a coach or a doctor. Use the live °C above: if it is very hot, humid, or stormy, keep it easy or rest."
    )
    return " ".join(bits)


def forecast_place(place: str, tomorrow: bool = False) -> str:
    phrase = f"weather in {place.strip()}"
    if tomorrow:
        phrase += " tomorrow"
    return forecast(phrase)


def forecast(user_text: str = "") -> str:
    place = _place_from(user_text)
    if not place:
        return (
            "I will not guess the weather. Say the town, for example: "
            "weather in Cape Town, or weather in Polokwane."
        )
    try:
        geo = _geocode(place)
        if not geo:
            return (
                f"I could not find a place called {place} in the weather atlas. "
                "Use a South African town name."
            )
        name, lat, lon, country = geo
        if _wants_tomorrow(user_text):
            daily = _daily(lat, lon)
            return _format_daily(name, country, daily)
        current = _current(lat, lon)
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return "The live weather feed is down. I will not invent a temperature. Try again in a minute."

    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    if temp is None:
        return f"Open-Meteo found {place} but sent no temperature. I will not guess."
    sky = WMO.get(int(current.get("weather_code") or 0), "conditions not listed in the weather code table")
    humidity = 0 if humidity is None else humidity
    wind = 0 if wind is None else wind
    where = name if country == "South Africa" else f"{name}, {country}"
    return (
        f"Live Open-Meteo reading for {where}: {temp:.0f}°C, {sky}. "
        f"Humidity {humidity:.0f}%, wind {wind:.0f} km/h. "
        "This is a measured feed, not a made-up number — forecasts can still change."
    )


def _wants_tomorrow(user_text: str) -> bool:
    text = (user_text or "").lower()
    return any(w in text for w in ("tomorrow", "ngomso", "ngomuso", "hosane", "ka moso"))


def _format_daily(name: str, country: str, daily: dict) -> str:
    times = daily.get("time") or []
    tmax = daily.get("temperature_2m_max") or []
    tmin = daily.get("temperature_2m_min") or []
    codes = daily.get("weather_code") or []
    if len(times) < 2 or len(tmax) < 2:
        return "Open-Meteo sent no tomorrow forecast. I will not invent one."
    sky = WMO.get(int(codes[1] or 0), "mixed conditions")
    where = name if country == "South Africa" else f"{name}, {country}"
    return (
        f"Live Open-Meteo forecast for {where} tomorrow ({times[1]}): "
        f"low {tmin[1]:.0f}°C, high {tmax[1]:.0f}°C, {sky}. "
        "This is a forecast, not a guarantee."
    )


def _place_from(user_text: str) -> str | None:
    text = (user_text or "").strip().lower()
    for nick, official in sorted(ALIASES.items(), key=lambda item: -len(item[0])):
        if re.search(rf"\b{re.escape(nick)}\b", text):
            return official

    match = re.search(
        r"\b(?:in|for|at|near|ku|e|ko|kwa)\s+([a-z][a-z\s'-]{1,40})\b",
        text,
    )
    if match:
        raw = match.group(1).strip(" ?.,!")
        raw = re.sub(
            r"\b(please|today|now|tomorrow|weather|forecast|temperature|weer|imozulu|a|an|the|my|our|run|jog|walk|trip|holiday|vacation|weekend|away|upcoming)\b",
            "",
            raw,
            flags=re.I,
        ).strip(" ?.,!")
        junk = {"run", "jog", "walk", "trip", "me", "you"}
        if raw and raw.lower() not in junk and len(raw) >= 3:
            return raw.title()

    return None


def _geocode(place: str) -> tuple[str, float, float, str] | None:
    with httpx.Client(timeout=15.0) as client:
        for extra in ({"countryCode": "ZA"}, {}):
            params = {"name": place, "count": 5, "language": "en", **extra}
            data = client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params=params,
            ).json()
            results = data.get("results") or []
            if not results:
                continue
            za = [r for r in results if r.get("country_code") == "ZA"]
            pick = za[0] if za else results[0]
            return (
                pick.get("name") or place,
                float(pick["latitude"]),
                float(pick["longitude"]),
                pick.get("country") or "",
            )
    return None


def _current(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "wind_speed_unit": "kmh",
        "timezone": "Africa/Johannesburg",
    }
    with httpx.Client(timeout=15.0) as client:
        data = client.get("https://api.open-meteo.com/v1/forecast", params=params).json()
    return data.get("current") or {}


def _daily(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "Africa/Johannesburg",
        "forecast_days": 3,
    }
    with httpx.Client(timeout=15.0) as client:
        data = client.get("https://api.open-meteo.com/v1/forecast", params=params).json()
    return data.get("daily") or {}
