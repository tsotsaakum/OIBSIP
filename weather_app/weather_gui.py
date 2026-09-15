"""Weather dashboard frontend (tkinter).

Layout is inspired by modern weather apps (large temperature, hourly strip,
daily list, metric tiles) without copying any product UI.

All API work stays in weather_service.py.
Run: python weather_gui.py
"""

from __future__ import annotations

import io
import os
import sys
import threading
import tkinter as tk
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageTk
from dotenv import load_dotenv

# Allow `python weather_gui.py` from any working directory.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from weather_service import (  # noqa: E402
    WeatherService,
    WeatherServiceError,
    format_degrees,
    format_pressure,
    format_wind,
    uv_level,
)

# Soft lavender dashboard — original palette, same information architecture.
BG = "#C9C3F2"
CARD = "#B0A8E6"
CARD_DEEP = "#9F96DC"
INK = "#FFFFFF"
SOFT = "#EDE9FF"
LINE = "#F6D56B"
RAIN = "#8ED0F8"
DANGER = "#FFE1E1"


class WeatherApp(tk.Tk):
    ICON_SM = (36, 36)
    ICON_MD = (44, 44)
    ICON_LG = (88, 88)

    def __init__(self, service: WeatherService):
        super().__init__()
        self.service = service
        self.unit = "C"
        self.current_weather = None
        self.hourly = None
        self.daily = None
        self._demo = False
        self._icon_bytes_map = {}
        self._icon_image_refs = []
        self._placeholder = "City or ZIP"
        self._hourly_points = []

        self.title("Weather")
        self.geometry("980x720")
        self.minsize(900, 660)
        self.configure(bg=BG)
        self._build()
        self._try_auto_detect_location()

    def _f(self, size, weight="normal"):
        return ("Segoe UI", size, weight)

    def _card(self, parent, **pack):
        frame = tk.Frame(parent, bg=CARD, padx=16, pady=14)
        frame.pack(**pack)
        return frame

    def _build(self):
        page = tk.Frame(self, bg=BG, padx=24, pady=18)
        page.pack(fill="both", expand=True)

        bar = tk.Frame(page, bg=BG)
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="Weather", font=self._f(13, "bold"), fg=INK, bg=BG).pack(side="left")

        self.unit_btn = tk.Button(
            bar, text="°C", font=self._f(11, "bold"), bg=CARD_DEEP, fg=INK,
            relief="flat", padx=12, pady=4, cursor="hand2", command=self.toggle_unit,
        )
        self.unit_btn.pack(side="right")

        self.search_btn = tk.Button(
            bar, text="Search", font=self._f(11, "bold"), bg=INK, fg="#5C5498",
            relief="flat", padx=14, pady=4, cursor="hand2", command=self.get_weather,
        )
        self.search_btn.pack(side="right", padx=(0, 8))

        self.city_entry = tk.Entry(
            bar, font=self._f(12), bg=CARD, fg=SOFT, insertbackground=INK,
            relief="flat", width=28,
        )
        self.city_entry.pack(side="right", ipady=6, padx=(0, 8))
        self.city_entry.insert(0, self._placeholder)
        self.city_entry.bind("<Return>", lambda _e: self.get_weather())
        self.city_entry.bind("<FocusIn>", self._focus_search)

        self.status = tk.Label(page, text="", font=self._f(10), fg=SOFT, bg=BG, anchor="w")
        self.status.pack(fill="x")
        self.error = tk.Label(page, text="", font=self._f(10), fg=DANGER, bg=BG, anchor="w")
        self.error.pack(fill="x")

        # Hero: oversized temperature + condition + icon
        hero = tk.Frame(page, bg=BG, pady=6)
        hero.pack(fill="x")
        hero_l = tk.Frame(hero, bg=BG)
        hero_l.pack(side="left", fill="x", expand=True)
        self.temp_lbl = tk.Label(hero_l, text="--°", font=("Segoe UI", 64, "bold"), fg=INK, bg=BG)
        self.temp_lbl.pack(anchor="w")
        self.cond_lbl = tk.Label(hero_l, text="Search a place to begin", font=self._f(16), fg=SOFT, bg=BG)
        self.cond_lbl.pack(anchor="w", pady=(0, 8))
        self.meta_lbl = tk.Label(hero_l, text="", font=self._f(11), fg=SOFT, bg=BG)
        self.meta_lbl.pack(anchor="w")
        self.place_lbl = tk.Label(hero_l, text="", font=self._f(12, "bold"), fg=INK, bg=BG)
        self.place_lbl.pack(anchor="w", pady=(6, 0))
        self.hero_icon = tk.Label(hero, bg=BG)
        self.hero_icon.pack(side="right", padx=(12, 8), pady=8)

        # Hourly strip + sparkline
        hourly_card = self._card(page, fill="x", pady=(14, 10))
        self.hourly_summary = tk.Label(
            hourly_card, text="Hourly forecast", font=self._f(11), fg=INK, bg=CARD, anchor="w", wraplength=860, justify="left",
        )
        self.hourly_summary.pack(fill="x")
        self.hourly_row = tk.Frame(hourly_card, bg=CARD)
        self.hourly_row.pack(fill="x", pady=(10, 0))
        self.spark = tk.Canvas(hourly_card, height=46, bg=CARD, highlightthickness=0)
        self.spark.pack(fill="x", pady=(2, 0))
        self.spark.bind("<Configure>", lambda _e: self._draw_spark())

        # Insight banner
        banner = tk.Frame(page, bg=CARD_DEEP, padx=16, pady=12)
        banner.pack(fill="x", pady=(0, 10))
        self.banner_title = tk.Label(banner, text="Outdoor note", font=self._f(12, "bold"), fg=INK, bg=CARD_DEEP)
        self.banner_title.pack()
        self.banner_body = tk.Label(banner, text="UV and wind tips appear after a search.", font=self._f(11), fg=SOFT, bg=CARD_DEEP)
        self.banner_body.pack()

        # Daily list + metric tiles
        bottom = tk.Frame(page, bg=BG)
        bottom.pack(fill="both", expand=True)

        daily_card = tk.Frame(bottom, bg=CARD, padx=12, pady=10)
        daily_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(daily_card, text="This week", font=self._f(10, "bold"), fg=SOFT, bg=CARD, anchor="w").pack(fill="x")
        self.daily_box = tk.Frame(daily_card, bg=CARD)
        self.daily_box.pack(fill="both", expand=True, pady=(6, 0))

        tiles = tk.Frame(bottom, bg=BG)
        tiles.pack(side="right", fill="both")
        self.tile_value = {}
        grid = (
            (0, 0, 1, "uv", "UV index"),
            (0, 1, 1, "humidity", "Humidity"),
            (1, 0, 1, "wind", "Wind"),
            (1, 1, 1, "pressure", "Pressure"),
            (2, 0, 1, "sunrise", "Sunrise"),
            (2, 1, 1, "sunset", "Sunset"),
        )
        for r, c, span, key, title in grid:
            cell = tk.Frame(tiles, bg=CARD, padx=14, pady=12, width=200, height=96)
            cell.grid(row=r, column=c, columnspan=span, padx=(0 if c else 0, 0 if span == 2 or c == 1 else 8),
                      pady=(0, 8) if r < 2 else (0, 0), sticky="nsew")
            cell.grid_propagate(False)
            tk.Label(cell, text=title, font=self._f(10), fg=SOFT, bg=CARD).pack()
            val = tk.Label(cell, text="—", font=self._f(16, "bold"), fg=INK, bg=CARD)
            val.pack(pady=(8, 0))
            self.tile_value[key] = val
        tiles.grid_rowconfigure(0, weight=1)
        tiles.grid_rowconfigure(1, weight=1)
        tiles.grid_rowconfigure(2, weight=1)
        tiles.grid_columnconfigure(0, weight=1)
        tiles.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.hourly_row, text="The next six hours will show here.", font=self._f(11), fg=SOFT, bg=CARD,
        ).pack(anchor="w")
        tk.Label(
            self.daily_box, text="Five-day outlook will show here.", font=self._f(11), fg=SOFT, bg=CARD,
        ).pack(anchor="w")

    def _focus_search(self, _e):
        if self.city_entry.get() == self._placeholder:
            self.city_entry.delete(0, "end")
            self.city_entry.config(fg=INK)

    def _query(self) -> str:
        text = self.city_entry.get().strip()
        return "" if text == self._placeholder else text

    def _try_auto_detect_location(self):
        def worker():
            city = self.service.detect_city_from_ip()
            if city:
                self.after(0, self._fill_city, city)

        threading.Thread(target=worker, daemon=True).start()

    def _fill_city(self, city: str):
        if self._query() == "":
            self.city_entry.delete(0, "end")
            self.city_entry.config(fg=INK)
            self.city_entry.insert(0, city)

    def get_weather(self):
        location = self._query()
        if not location:
            self.error.config(text="Please enter a city name or ZIP code.")
            return
        self.error.config(text="")
        self._set_loading(True)
        threading.Thread(target=self._fetch, args=(location,), daemon=True).start()

    def _fetch(self, location: str):
        try:
            bundle = self.service.get_bundle(location)
            current = bundle.current
            hourly = WeatherService.get_next_6_hours(bundle)
            daily = WeatherService.get_next_5_days(bundle)
            codes = {current.icon}
            codes.update(p.icon for p in hourly)
            codes.update(p.icon for p in daily)
            codes.update(p.night_icon for p in daily if p.night_icon)
            icons = {code: self.service.fetch_icon_bytes(code) or None for code in codes if code}
            self.after(0, self._on_ok, current, hourly, daily, icons, bundle.demo)
        except WeatherServiceError as exc:
            self.after(0, self._on_err, str(exc))
        except Exception as exc:  # noqa: BLE001
            self.after(0, self._on_err, f"Unexpected error: {exc}")

    def _on_ok(self, current, hourly, daily, icons, demo=False):
        self.current_weather = current
        self.hourly = hourly
        self.daily = daily
        self._icon_bytes_map = icons
        self._icon_image_refs = []
        self._demo = demo
        self._set_loading(False)
        if demo:
            self.status.config(text="Demo mode — add an API key to .env for live weather.")
        self._paint()

    def _on_err(self, message: str):
        self._set_loading(False)
        self.error.config(text=message)

    def _deg(self, celsius: float) -> str:
        return format_degrees(celsius, self.unit)

    def _tz(self):
        offset = getattr(self.current_weather, "timezone_offset", 0) or 0
        return timezone(timedelta(seconds=offset))

    def _hm(self, epoch: int) -> str:
        if not epoch:
            return "—"
        return datetime.fromtimestamp(epoch, tz=self._tz()).strftime("%I:%M %p").lstrip("0")

    def _paint(self):
        data = self.current_weather
        if data is None:
            return
        self.place_lbl.config(text=data.place_label)
        self.temp_lbl.config(text=self._deg(data.temp_c))
        self.cond_lbl.config(text=data.description)
        self.meta_lbl.config(
            text=f"{self._deg(data.max_c)} / {self._deg(data.min_c)}   Feels like {self._deg(data.feels_like_c)}"
        )
        self._icon(self.hero_icon, data.icon, self.ICON_LG)

        uv_txt = uv_level(data.uv_index)
        self.banner_title.config(text="Time outdoors")
        self.banner_body.config(text=f"UV is {uv_txt.lower()} today. {format_wind(data.wind_mps, self.unit)} wind.")

        self.tile_value["uv"].config(text=f"{data.uv_index:.0f}\n{uv_txt}")
        self.tile_value["humidity"].config(text=f"{data.humidity}%")
        self.tile_value["wind"].config(text=format_wind(data.wind_mps, self.unit))
        self.tile_value["pressure"].config(text=format_pressure(data.pressure_hpa))
        self.tile_value["sunrise"].config(text=self._hm(data.sunrise_epoch))
        self.tile_value["sunset"].config(text=self._hm(data.sunset_epoch))

        self._paint_hourly()
        self._paint_daily()
        self.unit_btn.config(text=f"°{self.unit}")

    def _paint_hourly(self):
        for child in self.hourly_row.winfo_children():
            child.destroy()
        self.spark.delete("all")
        points = list(self.hourly or [])
        if not points:
            return

        first = points[0]
        self.hourly_summary.config(
            text=f"{first.description}. About {self._deg(max(p.temp_c for p in points))} at the warmest hour."
        )

        tz = self._tz()
        cols = []
        for i, point in enumerate(points):
            col = tk.Frame(self.hourly_row, bg=CARD)
            col.pack(side="left", fill="both", expand=True)
            cols.append(col)
            when = "Now" if i == 0 else datetime.fromtimestamp(point.epoch, tz=tz).strftime("%I %p").lstrip("0")
            tk.Label(col, text=when, font=self._f(9, "bold"), fg=SOFT, bg=CARD).pack()
            icon = tk.Label(col, bg=CARD)
            icon.pack(pady=2)
            self._icon(icon, point.icon, self.ICON_MD)
            tk.Label(col, text=self._deg(point.temp_c), font=self._f(12, "bold"), fg=INK, bg=CARD).pack()

        self._hourly_points = points
        self.update_idletasks()
        self._draw_spark()
        for col, point in zip(cols, points):
            chance = f"{round(point.pop * 100)}%"
            tk.Label(col, text=chance, font=self._f(9), fg=RAIN, bg=CARD).pack()

    def _draw_spark(self):
        self.spark.delete("all")
        points = getattr(self, "_hourly_points", None) or []
        if len(points) < 2:
            return
        width = max(self.spark.winfo_width(), 200)
        height = 46
        temps = [p.temp_c for p in points]
        lo, hi = min(temps), max(temps)
        span = max(hi - lo, 1.0)
        xs, ys = [], []
        n = len(points)
        for i, temp in enumerate(temps):
            x = 28 + (width - 56) * (i / max(n - 1, 1))
            y = 8 + (height - 18) * (1 - (temp - lo) / span)
            xs.append(x)
            ys.append(y)
        flat = [v for pair in zip(xs, ys) for v in pair]
        self.spark.create_line(*flat, fill=LINE, width=2, smooth=True)
        for x, y in zip(xs, ys):
            self.spark.create_oval(x - 3, y - 3, x + 3, y + 3, fill=LINE, outline="")

    def _paint_daily(self):
        for child in self.daily_box.winfo_children():
            child.destroy()
        for day in self.daily or []:
            row = tk.Frame(self.daily_box, bg=CARD, pady=5)
            row.pack(fill="x")
            tk.Label(row, text=day.date_label, font=self._f(12), fg=INK, bg=CARD, width=11, anchor="w").pack(side="left")
            tk.Label(row, text=f"{round(day.pop * 100)}%", font=self._f(10), fg=RAIN, bg=CARD, width=5).pack(side="left")
            day_icon = tk.Label(row, bg=CARD)
            day_icon.pack(side="left", padx=4)
            self._icon(day_icon, day.icon, self.ICON_SM)
            night_icon = tk.Label(row, bg=CARD)
            night_icon.pack(side="left", padx=2)
            self._icon(night_icon, day.night_icon or day.icon, self.ICON_SM)
            tk.Label(
                row, text=f"{self._deg(day.max_c)}  {self._deg(day.min_c)}",
                font=self._f(12, "bold"), fg=INK, bg=CARD,
            ).pack(side="right")

    def _icon(self, label, code, size):
        raw = self._icon_bytes_map.get(code)
        if not raw:
            label.config(image="", text="")
            return
        image = Image.open(io.BytesIO(raw)).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self._icon_image_refs.append(photo)
        label.config(image=photo, text="")

    def toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.unit_btn.config(text=f"°{self.unit}")
        if self.current_weather is not None:
            self._icon_image_refs = []
            self._paint()

    def _set_loading(self, busy: bool):
        self.search_btn.config(state="disabled" if busy else "normal")
        if busy:
            self.status.config(text="Updating…")
        elif not self._demo:
            self.status.config(text="")


def main():
    load_dotenv(Path(__file__).resolve().parent / ".env")
    load_dotenv()
    key = os.environ.get("OPENWEATHERMAP_API_KEY") or os.environ.get("OPENWEATHER_API_KEY")
    WeatherApp(WeatherService(api_key=key)).mainloop()


def run_gui():
    main()


if __name__ == "__main__":
    main()
