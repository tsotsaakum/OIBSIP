"""Local preview for the Lentswe web app (no PHP required).

PHP file weather.php is still the assignment backend. This helper serves
the same HTML/CSS/JS and answers /weather.php using weather_service.py.
"""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from weather_service import WeatherError, WeatherService  # noqa: E402


def bundle_to_json(bundle) -> dict:
    c = bundle.current
    return {
        "ok": True,
        "demo": bundle.demo,
        "current": {
            "place": c.place_label,
            "description": c.description,
            "icon": c.icon,
            "temp_c": c.temp_c,
            "feels_like_c": c.feels_like_c,
            "humidity": c.humidity,
            "wind_mps": c.wind_mps,
            "pressure_hpa": c.pressure_hpa,
            "uv_index": c.uv_index,
            "timezone_offset": c.timezone_offset,
            "sunrise_epoch": c.sunrise_epoch,
            "sunset_epoch": c.sunset_epoch,
            "min_c": c.min_c,
            "max_c": c.max_c,
        },
        "hourly": [
            {"epoch": h.epoch, "temp_c": h.temp_c, "description": h.description, "icon": h.icon, "pop": h.pop}
            for h in bundle.hourly
        ],
        "daily": [
            {
                "date_label": d.date_label,
                "min_c": d.min_c,
                "max_c": d.max_c,
                "description": d.description,
                "icon": d.icon,
                "night_icon": d.night_icon,
                "pop": d.pop,
            }
            for d in bundle.daily
        ],
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.endswith("weather.php"):
            self._weather(parse_qs(parsed.query))
            return
        super().do_GET()

    def _weather(self, qs):
        service = WeatherService()
        try:
            if "ip" in qs:
                payload = {"ok": True, "city": service.detect_city_from_ip()}
            else:
                q = (qs.get("q") or [""])[0].strip()
                if not q:
                    self._json(400, {"ok": False, "error": "Please enter a city name or ZIP code."})
                    return
                payload = bundle_to_json(service.get_bundle(q))
            self._json(200, payload)
        except WeatherError as exc:
            self._json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"ok": False, "error": str(exc)})

    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = 8080
    print(f"Lentswe -> http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
