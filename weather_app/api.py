"""Compatibility module for `import api`.

The live OpenWeatherMap calls, demo data, and data types all live in
`weather_service.py`. CLI and GUI should import from there.

This file exists so older notes that say `from api import WeatherService`
still work.
"""

from weather_service import (
    CityNotFoundError,
    CurrentWeather,
    DailyPoint,
    EmptyInputError,
    HourlyPoint,
    InvalidApiKeyError,
    NetworkError,
    NetworkTimeoutError,
    WeatherBundle,
    WeatherError,
    WeatherService,
    WeatherServiceError,
    fetch_weather,
    format_pressure,
    format_temp,
    format_wind,
    looks_like_zip,
    validate_query,
)

__all__ = [
    "CityNotFoundError",
    "CurrentWeather",
    "DailyPoint",
    "EmptyInputError",
    "HourlyPoint",
    "InvalidApiKeyError",
    "NetworkError",
    "NetworkTimeoutError",
    "WeatherBundle",
    "WeatherError",
    "WeatherService",
    "WeatherServiceError",
    "fetch_weather",
    "format_pressure",
    "format_temp",
    "format_wind",
    "looks_like_zip",
    "validate_query",
]
