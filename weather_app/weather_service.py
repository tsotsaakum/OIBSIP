"""Shared weather backend for the CLI and GUI.

This module exists so *neither frontend* talks to OpenWeatherMap directly.
Both `weather_cli.py` and `weather_gui.py` call `WeatherService`. If the API
changes, you only edit this file.

Typical flow:
    service = WeatherService()          # reads OPENWEATHERMAP_API_KEY / .env
    bundle = service.get_bundle("Paris")
    print(bundle.current.temp_c)
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):
        return False

# Load `.env` from this folder (project root) and the parent folder if present.
_here = Path(__file__).resolve().parent
load_dotenv(_here / ".env")
load_dotenv(_here.parent / ".env")

OWM_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
OWM_ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"
IPINFO_URL = "https://ipinfo.io/json"
DEFAULT_TIMEOUT = 8
# 4-digit codes (e.g. South Africa) are city/postal queries, not US ZIPs.
US_ZIP_RE = re.compile(r"^\d{5}(?:-\d{4})?$")
ZIP_WITH_COUNTRY_RE = re.compile(r"^\d{4,10}\s*,\s*[A-Za-z]{2}$")
ZIP_RE = re.compile(r"^(?:\d{5}(?:-\d{4})?|\d{4,10}\s*,\s*[A-Za-z]{2})$")


# ---------------------------------------------------------------------------
# Exceptions — frontends catch these instead of raw requests errors
# ---------------------------------------------------------------------------

class WeatherError(Exception):
    """User-facing weather error. Message is safe to show in CLI or GUI."""


class EmptyInputError(WeatherError):
    def __init__(self) -> None:
        super().__init__("Enter a city name or ZIP code.")


class CityNotFoundError(WeatherError):
    def __init__(self, query: str) -> None:
        super().__init__(f'No weather found for "{query}". Check the spelling or try a nearby city.')


class InvalidApiKeyError(WeatherError):
    def __init__(self) -> None:
        super().__init__(
            "The OpenWeatherMap API key is invalid. Put a free key in the .env file "
            "as OPENWEATHERMAP_API_KEY, or leave it blank to use demo mode."
        )


class NetworkTimeoutError(WeatherError):
    def __init__(self) -> None:
        super().__init__("The weather service timed out. Check your connection and try again.")


class NetworkError(WeatherError):
    def __init__(self, detail: str = "") -> None:
        message = "Could not reach the weather service."
        if detail:
            message = f"{message} {detail}"
        super().__init__(message)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def c_to_f(celsius: float) -> float:
    return celsius * 9.0 / 5.0 + 32.0


def format_temp(celsius: float, unit: str) -> str:
    if unit.upper() == "F":
        return f"{round(c_to_f(celsius))}°F"
    return f"{round(celsius)}°C"


def format_degrees(celsius: float, unit: str) -> str:
    """Dashboard style: 75° rather than 75°F (the toggle already shows the unit)."""
    if unit.upper() == "F":
        return f"{round(c_to_f(celsius))}°"
    return f"{round(celsius)}°"


def format_pressure(hpa: int) -> str:
    return f"{int(hpa)} hPa"


def format_wind(mps: float, unit: str) -> str:
    if unit.upper() == "F":
        return f"{mps * 2.23694:.0f} mph"
    return f"{mps:.1f} m/s"


def uv_level(index: float) -> str:
    if index < 3:
        return "Low"
    if index < 6:
        return "Moderate"
    if index < 8:
        return "High"
    return "Very high"


def estimate_uv(icon: str) -> float:
    """Free weather endpoint has no UV; we estimate from the icon so the UI can show a tile."""
    return {
        "01": 8.0,
        "02": 5.5,
        "03": 4.0,
        "04": 3.0,
        "09": 2.0,
        "10": 2.5,
        "11": 2.0,
        "13": 3.5,
        "50": 2.0,
    }.get((icon or "01d")[:2], 4.0)


# ---------------------------------------------------------------------------
# Data shapes returned to both frontends
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CurrentWeather:
    location_name: str
    country: str
    description: str
    icon: str
    temp_c: float
    feels_like_c: float
    humidity: int
    wind_mps: float
    pressure_hpa: int = 0
    timezone_offset: int = 0
    sunrise_epoch: int = 0
    sunset_epoch: int = 0
    min_c: float = 0.0
    max_c: float = 0.0
    uv_index: float = 0.0
    wind_deg: float = 0.0

    @property
    def place_label(self) -> str:
        if self.country:
            return f"{self.location_name}, {self.country}"
        return self.location_name


@dataclass(frozen=True)
class HourlyPoint:
    epoch: int
    temp_c: float
    description: str
    icon: str
    humidity: int
    wind_mps: float
    pop: float = 0.0


@dataclass(frozen=True)
class DailyPoint:
    date_label: str
    epoch: int
    min_c: float
    max_c: float
    description: str
    icon: str
    night_icon: str = ""
    pop: float = 0.0


@dataclass(frozen=True)
class WeatherBundle:
    """Everything one screen needs after a single user search."""

    current: CurrentWeather
    hourly: list[HourlyPoint] = field(default_factory=list)
    daily: list[DailyPoint] = field(default_factory=list)
    demo: bool = False


def validate_query(raw: str) -> str:
    query = (raw or "").strip()
    if not query:
        raise EmptyInputError()
    return query


def looks_like_zip(query: str) -> bool:
    text = (query or "").strip()
    return bool(US_ZIP_RE.match(text) or ZIP_WITH_COUNTRY_RE.match(text))


def _clean_api_key(value: str | None) -> str:
    key = (value or "").strip().strip("'").strip('"').strip()
    if key.lower() in {"", "your_key_here", "changeme", "none", "null"}:
        return ""
    return key


def parse_current(payload: dict) -> CurrentWeather:
    weather = (payload.get("weather") or [{}])[0]
    main = payload.get("main") or {}
    wind = payload.get("wind") or {}
    sys = payload.get("sys") or {}
    icon = str(weather.get("icon") or "01d")
    temp = float(main.get("temp", 0))
    return CurrentWeather(
        location_name=str(payload.get("name") or "Unknown"),
        country=str(sys.get("country") or ""),
        description=str(weather.get("description") or "Unknown").capitalize(),
        icon=icon,
        temp_c=temp,
        feels_like_c=float(main.get("feels_like", temp)),
        humidity=int(main.get("humidity", 0)),
        wind_mps=float(wind.get("speed", 0)),
        pressure_hpa=int(main.get("pressure", 0)),
        timezone_offset=int(payload.get("timezone") or 0),
        sunrise_epoch=int(sys.get("sunrise") or 0),
        sunset_epoch=int(sys.get("sunset") or 0),
        min_c=float(main.get("temp_min", temp)),
        max_c=float(main.get("temp_max", temp)),
        uv_index=estimate_uv(icon),
        wind_deg=float(wind.get("deg", 0)),
    )


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def next_six_hours(
    current: CurrentWeather,
    forecast_list: list[dict],
    now_epoch: int | None = None,
) -> list[HourlyPoint]:
    """Turn 3-hour forecast steps into six hourly points (now + next 5 hours).

    The free `/forecast` feed only has 3-hour buckets. We take the first couple
    of future entries and interpolate so the dashboard can show an hourly strip.
    """
    now = now_epoch if now_epoch is not None else int(datetime.now(timezone.utc).timestamp())
    anchors: list[tuple] = [
        (now, current.temp_c, current.description, current.icon, current.humidity, current.wind_mps, 0.0)
    ]
    for item in forecast_list:
        dt = int(item.get("dt") or 0)
        if dt <= now:
            continue
        weather = (item.get("weather") or [{}])[0]
        main = item.get("main") or {}
        wind = item.get("wind") or {}
        anchors.append(
            (
                dt,
                float(main.get("temp", current.temp_c)),
                str(weather.get("description") or current.description).capitalize(),
                str(weather.get("icon") or current.icon),
                int(main.get("humidity", current.humidity)),
                float(wind.get("speed", current.wind_mps)),
                float(item.get("pop") or 0.0),
            )
        )
        if len(anchors) >= 4:  # current + two 3-hour steps is enough to cover 6 hours
            break

    points: list[HourlyPoint] = []
    for hour in range(0, 6):
        target = now + 3600 * hour
        if len(anchors) == 1:
            points.append(
                HourlyPoint(target, current.temp_c, current.description, current.icon, current.humidity, current.wind_mps, 0.0)
            )
            continue
        left, right = anchors[0], anchors[-1]
        for i in range(len(anchors) - 1):
            if anchors[i][0] <= target <= anchors[i + 1][0]:
                left, right = anchors[i], anchors[i + 1]
                break
        span = max(1, right[0] - left[0])
        t = min(1.0, max(0.0, (target - left[0]) / span))
        nearer = left if t < 0.5 else right
        points.append(
            HourlyPoint(
                epoch=target,
                temp_c=round(_lerp(left[1], right[1], t), 1),
                description=nearer[2],
                icon=nearer[3],
                humidity=(round(_lerp(left[4], right[4], t))),
                wind_mps=round(_lerp(left[5], right[5], t), 1),
                pop=round(_lerp(left[6], right[6], t), 2),
            )
        )
    return points


def next_five_days(forecast_list: list[dict], timezone_offset: int = 0) -> list[DailyPoint]:
    """One row per calendar day, using the slot closest to midday."""
    tz = timezone(timedelta(seconds=timezone_offset))
    today = datetime.now(tz).date()
    buckets: dict = defaultdict(list)
    for item in forecast_list:
        dt = datetime.fromtimestamp(int(item.get("dt") or 0), tz=timezone.utc).astimezone(tz)
        if dt.date() < today:
            continue
        buckets[dt.date()].append(item)

    daily: list[DailyPoint] = []
    for day in sorted(buckets.keys())[:5]:
        items = buckets[day]
        temps = [float((i.get("main") or {}).get("temp", 0)) for i in items]
        pops = [float(i.get("pop") or 0) for i in items]
        midday = min(
            items,
            key=lambda i: abs(datetime.fromtimestamp(i["dt"], tz=timezone.utc).astimezone(tz).hour - 12),
        )
        night = min(
            items,
            key=lambda i: -datetime.fromtimestamp(i["dt"], tz=timezone.utc).astimezone(tz).hour,
        )
        weather = (midday.get("weather") or [{}])[0]
        night_weather = (night.get("weather") or [{}])[0]
        label = "Today" if day == today else datetime.combine(day, datetime.min.time()).strftime("%A")
        daily.append(
            DailyPoint(
                date_label=label,
                epoch=int(datetime.combine(day, datetime.min.time(), tzinfo=tz).timestamp()),
                min_c=min(temps) if temps else 0.0,
                max_c=max(temps) if temps else 0.0,
                description=str(weather.get("description") or "").capitalize(),
                icon=str(weather.get("icon") or "01d"),
                night_icon=str(night_weather.get("icon") or "01n"),
                pop=max(pops) if pops else 0.0,
            )
        )
    return daily


def _demo_bundle(query: str) -> WeatherBundle:
    """Deterministic fake weather so the UI works before an API key is issued."""
    conditions = [
        ("Clear sky", "01d"),
        ("Few clouds", "02d"),
        ("Scattered clouds", "03d"),
        ("Broken clouds", "04d"),
        ("Light rain", "10d"),
        ("Rain", "09d"),
        ("Thunderstorm", "11d"),
        ("Snow", "13d"),
        ("Mist", "50d"),
        ("Partly cloudy", "02d"),
        ("Haze", "50d"),
    ]
    digest = hashlib.sha256(query.strip().lower().encode()).hexdigest()
    seed = int(digest[:8], 16)
    now = datetime.now(timezone.utc)
    base = 8 + (seed % 22)
    humidity = 35 + (seed % 50)
    wind = 1.5 + (seed % 80) / 10.0
    desc, icon = conditions[seed % len(conditions)]
    place = query.strip().title()
    country = "US" if query.strip().isdigit() else ""
    current = CurrentWeather(
        location_name=place,
        country=country,
        description=desc,
        icon=icon,
        temp_c=float(base),
        feels_like_c=float(base - 1 + (seed % 4) / 2),
        humidity=humidity,
        wind_mps=wind,
        pressure_hpa=1000 + (seed % 31),
        sunrise_epoch=int(now.replace(hour=6, minute=55, second=0, microsecond=0).timestamp()),
        sunset_epoch=int(now.replace(hour=17, minute=40, second=0, microsecond=0).timestamp()),
        min_c=float(base - 5),
        max_c=float(base + 4),
        uv_index=estimate_uv(icon),
        wind_deg=float((seed * 17) % 360),
    )
    hourly = []
    for hour in range(6):
        swing = 3 * math.sin((seed % 7 + hour) / 3)
        h_desc, h_icon = conditions[(seed + hour * 3) % len(conditions)]
        hourly.append(
            HourlyPoint(
                epoch=int((now + timedelta(hours=hour)).timestamp()),
                temp_c=float(base) if hour == 0 else round(base + swing, 1),
                description=desc if hour == 0 else h_desc,
                icon=icon if hour == 0 else h_icon,
                humidity=min(95, max(20, humidity + hour - 3)),
                wind_mps=round(max(0.4, wind + (hour % 3) * 0.4), 1),
                pop=round(min(0.9, (seed % 10) / 30 + hour * 0.04), 2),
            )
        )
    daily = []
    for day in range(5):
        d_desc, d_icon = conditions[(seed + day * 4) % len(conditions)]
        day_dt = now + timedelta(days=day)
        daily.append(
            DailyPoint(
                date_label="Today" if day == 0 else day_dt.strftime("%A"),
                epoch=int(day_dt.timestamp()),
                min_c=float(base - 4 + (day % 3)),
                max_c=float(base + 3 + ((seed + day) % 4)),
                description=d_desc,
                icon=d_icon,
                night_icon=d_icon.replace("d", "n"),
                pop=round(min(0.8, (seed % 8) / 20 + day * 0.03), 2),
            )
        )
    return WeatherBundle(current=current, hourly=hourly, daily=daily, demo=True)


def _demo_forecast_list(query: str) -> list[dict]:
    """OWM-shaped 3-hour slots so get_forecast() still works in demo mode."""
    bundle = _demo_bundle(query)
    now = int(datetime.now(timezone.utc).timestamp())
    items: list[dict] = []
    for i in range(40):
        hour = bundle.hourly[i % len(bundle.hourly)]
        day = bundle.daily[min(i // 8, len(bundle.daily) - 1)]
        use_hour = i < 8
        temp = hour.temp_c if use_hour else (day.min_c + day.max_c) / 2.0
        desc = hour.description if use_hour else day.description
        icon = hour.icon if use_hour else day.icon
        dt = now + i * 3 * 3600
        items.append(
            {
                "dt": dt,
                "main": {"temp": temp, "feels_like": temp, "humidity": hour.humidity},
                "weather": [{"description": desc.lower(), "icon": icon}],
                "wind": {"speed": hour.wind_mps},
                "pop": hour.pop if use_hour else day.pop,
                "dt_txt": datetime.fromtimestamp(dt, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return items


class WeatherService:
    """Thin wrapper around OpenWeatherMap + ipinfo.

    Both frontends should create one instance and call methods on it. They
    should not import `requests` themselves.
    """

    def __init__(self, api_key: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.api_key = _clean_api_key(api_key)
        if not self.api_key:
            self.api_key = _clean_api_key(os.environ.get("OPENWEATHERMAP_API_KEY")) or _clean_api_key(
                os.environ.get("OPENWEATHER_API_KEY")
            )
        key_file = Path.home() / ".skycast_api_key"
        if not self.api_key and key_file.is_file():
            self.api_key = _clean_api_key(key_file.read_text(encoding="utf-8"))

    @staticmethod
    def get_icon_url(icon_code: str) -> str:
        return OWM_ICON_URL.format(icon=icon_code or "01d")

    def _params(self, location: str) -> dict[str, str]:
        params = {"appid": self.api_key, "units": "metric"}
        if looks_like_zip(location):
            zip_code = location.replace(" ", "")
            if "," in zip_code:
                params["zip"] = zip_code
            else:
                params["zip"] = f"{zip_code.split('-')[0]},US"
        else:
            params["q"] = location
        return params

    def _get(self, url: str, params: dict | None = None) -> requests.Response:
        try:
            return requests.get(url, params=params, timeout=self.timeout)
        except requests.Timeout as exc:
            raise NetworkTimeoutError() from exc
        except requests.RequestException as exc:
            raise NetworkError(str(exc)) from exc

    def _raise_for_status(self, response: requests.Response, query: str) -> None:
        if response.status_code == 401:
            raise InvalidApiKeyError()
        if response.status_code == 404:
            raise CityNotFoundError(query)
        if response.status_code >= 400:
            try:
                message = response.json().get("message", response.text)
            except ValueError:
                message = response.text
            raise NetworkError(str(message))

    def get_current_weather(self, location: str) -> CurrentWeather:
        """GET /data/2.5/weather — current conditions for a city or ZIP."""
        cleaned = validate_query(location)
        if not self.api_key:
            return _demo_bundle(cleaned).current
        response = self._get(OWM_WEATHER_URL, self._params(cleaned))
        self._raise_for_status(response, cleaned)
        return parse_current(response.json())

    def get_forecast(self, location: str) -> list[dict]:
        """GET /data/2.5/forecast — 3-hour steps for about five days."""
        cleaned = validate_query(location)
        if not self.api_key:
            return _demo_forecast_list(cleaned)
        response = self._get(OWM_FORECAST_URL, self._params(cleaned))
        self._raise_for_status(response, cleaned)
        return list(response.json().get("list") or [])

    def get_bundle(self, location: str) -> WeatherBundle:
        """One call used by both UIs: current + hourly strip + daily list."""
        cleaned = validate_query(location)
        if cleaned.lower() in {"timeout", "simulate-timeout"}:
            raise NetworkTimeoutError()
        if cleaned.lower() in {"notfound", "nowhere"}:
            raise CityNotFoundError(cleaned)
        if not self.api_key:
            return _demo_bundle(cleaned)

        current = self.get_current_weather(cleaned)
        forecast = self.get_forecast(cleaned)
        return WeatherBundle(
            current=current,
            hourly=next_six_hours(current, forecast),
            daily=next_five_days(forecast, current.timezone_offset),
            demo=False,
        )

    def detect_city_from_ip(self) -> str | None:
        """Best-effort city from ipinfo.io. Returns None on failure — never crashes."""
        try:
            response = self._get(IPINFO_URL)
            if response.status_code >= 400:
                return None
            data = response.json()
            city = str(data.get("city") or "").strip()
            country = str(data.get("country") or "").strip()
            if city and country:
                return f"{city},{country}"
            return city or None
        except WeatherError:
            return None
        except ValueError:
            return None

    def fetch_icon_bytes(self, icon_code: str) -> bytes:
        try:
            response = self._get(self.get_icon_url(icon_code))
            if response.status_code >= 400 or not response.content:
                return b""
            return response.content
        except WeatherError:
            return b""

    @staticmethod
    def get_next_6_hours(hourly) -> list:
        """Assignment helper: next 6 hours (HourlyPoint list, WeatherBundle, or OWM list)."""
        if hasattr(hourly, "hourly"):
            return list(hourly.hourly)
        items = list(hourly or [])
        if items and isinstance(items[0], dict) and "weather" in items[0]:
            seed = items[0]
            current = parse_current(
                {"name": "Unknown", "weather": seed.get("weather"), "main": seed.get("main"), "wind": seed.get("wind"), "dt": seed.get("dt")}
            )
            return next_six_hours(current, items, now_epoch=int(seed.get("dt") or 0))
        return items

    @staticmethod
    def get_next_5_days(daily) -> list:
        """Assignment helper: next 5 days (DailyPoint list, WeatherBundle, or OWM list)."""
        if hasattr(daily, "daily"):
            return list(daily.daily)[:5]
        items = list(daily or [])
        if items and isinstance(items[0], dict) and "dt" in items[0]:
            offset = 0
            first = items[0]
            if isinstance(first.get("timezone"), int):
                offset = first["timezone"]
            return next_five_days(items, offset)[:5]
        return items[:5]


# Alias used by the GUI / assignment write-ups.
WeatherServiceError = WeatherError

build_hourly = next_six_hours
build_daily = next_five_days


def fetch_weather(query: str, api_key: str | None = None) -> WeatherBundle:
    return WeatherService(api_key=api_key).get_bundle(query)
