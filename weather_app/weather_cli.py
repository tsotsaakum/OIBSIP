"""Beginner frontend: a command-line weather lookup.

All HTTP work lives in weather_service.py. This file only:
  1. asks the user for a city
  2. calls WeatherService
  3. prints a friendly summary (or a friendly error)
"""

from datetime import datetime, timedelta, timezone

from weather_service import (
    EmptyInputError,
    WeatherError,
    WeatherService,
    format_temp,
    format_wind,
)


def _print_bundle(bundle, unit: str = "C") -> None:
    current = bundle.current
    demo = " (demo data — add OPENWEATHERMAP_API_KEY to .env for live weather)" if bundle.demo else ""
    print(f"Weather for {current.place_label}{demo}")
    print(f"  Conditions  : {current.description}")
    print(f"  Temperature : {format_temp(current.temp_c, 'C')} / {format_temp(current.temp_c, 'F')}")
    print(f"  Feels like  : {format_temp(current.feels_like_c, unit)}")
    print(f"  Humidity    : {current.humidity}%")
    print(f"  Pressure    : {current.pressure_hpa} hPa")
    print(f"  Wind        : {format_wind(current.wind_mps, unit)}")

    if bundle.hourly:
        print("  Next 6 hours:")
        tz = timezone(timedelta(seconds=current.timezone_offset or 0))
        for point in bundle.hourly:
            stamp = datetime.fromtimestamp(point.epoch, tz=tz).strftime("%H:%M")
            print(f"    {stamp}  {format_temp(point.temp_c, unit)}  {point.description}")

    if bundle.daily:
        print("  Next 5 days:")
        for day in bundle.daily:
            print(
                f"    {day.date_label:<10}  "
                f"{format_temp(day.min_c, unit)} / {format_temp(day.max_c, unit)}  "
                f"{day.description}"
            )


def run_cli(city=None, use_ip=False, loop=False) -> int:
    service = WeatherService()

    def lookup(query: str) -> int:
        try:
            bundle = service.get_bundle(query)
        except EmptyInputError as exc:
            print(f"Error: {exc}")
            return 2
        except WeatherError as exc:
            print(f"Error: {exc}")
            return 1
        _print_bundle(bundle)
        return 0

    if use_ip and not city:
        city = service.detect_city_from_ip()
        if not city:
            print("Error: Could not detect city from IP.")
            return 1
        print(f"Detected location: {city}")

    if city:
        return lookup(city)

    last_code = 0
    while True:
        query = input("City name or ZIP code (q to quit): ").strip()
        if query.lower() in {"q", "quit", "exit"}:
            return last_code
        last_code = lookup(query)
        if not loop:
            return last_code


if __name__ == "__main__":
    raise SystemExit(run_cli(loop=True))
