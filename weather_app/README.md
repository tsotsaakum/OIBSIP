# Lentswe — weather, in your own words

OIBSIP intern project: one weather backend, three ways to use it.

- **Lentswe** (`web/`) — HTML, CSS, JavaScript, PHP. Search a city, hear the forecast, speak a place name.
- **CLI** (`weather_cli.py`) — type a city or ZIP and print a summary
- **Python GUI** (`weather_gui.py`) — Tkinter dashboard
- **Backend** (`weather_service.py`) — OpenWeatherMap, errors, and demo data

The web app never sees the API key. PHP (or `web/serve.py`) keeps it on the server. The Python GUI and CLI only talk to `WeatherService`.

---

## Features

- Search by **city name** or **ZIP** (`90210` = US ZIP; `8000,ZA` = ZIP with country)
- Current temperature, feels like, description, humidity, wind
- Next **6 hours** (icons, temps, rain chance, temperature line)
- Next **5 days** (high / low, day and night icons, rain chance)
- Extra tiles: UV, humidity, wind, **pressure**, sunrise / sunset
- Celsius / Fahrenheit toggle (no extra API call)
- Automatic city fill from IP (ipinfo.io) when the window opens
- **Demo mode** if no API key is set (app still runs)

---

## Setup

Python 3.10+ recommended.

```text
cd weather_app
pip install -r requirements.txt
```

Dependencies: `requests`, `python-dotenv`, `pillow`.

### API key

1. Create a free key: https://home.openweathermap.org/api_keys  
   Sign up: https://home.openweathermap.org/users/sign_up
2. Copy `.env.example` to `.env` in this folder.
3. Put your key on one line (either name works):

```text
OPENWEATHERMAP_API_KEY=your_key_here
```

A new OpenWeatherMap key can take a few minutes to activate. **Do not commit `.env`.** It is listed in `.gitignore`.

If `.env` is missing or the key is blank, the app uses demo weather.

---

## How to run

GUI (default):

```text
python weather_gui.py
```

or

```text
python main.py
```

CLI:

```text
python weather_cli.py
python main.py --cli
python main.py --cli --city London
python main.py --cli --ip
```

Type `q` in the CLI loop to quit.

### Lentswe (HTML / CSS / JS / PHP)

Needs PHP on your PATH. From the `web` folder:

```text
cd web
php -S localhost:8080
```

Then open http://localhost:8080

- Mic button: speak a city name (Chrome or Edge)
- Speaker button: Lentswe reads the forecast aloud
If PHP is not installed, preview with Python (same pages):

```text
python web/serve.py
```

Then open http://127.0.0.1:8080


---

## Project files

| File | What it is |
|------|------------|
| `weather_service.py` | Backend: API, demo data, ZIP rules, forecast helpers |
| `weather_gui.py` | Advanced-tier dashboard UI |
| `weather_cli.py` | Beginner-tier command-line UI |
| `api.py` | Optional `from api import WeatherService` |
| `web/` | Lentswe site (`index.html`, CSS, JS, `weather.php`) |
| `web/serve.py` | Local preview if PHP is not installed |
| `main.py` / `_main_.py` | Launcher (`--cli`, `--city`, `--ip`, `--gui`) |
| `.env.example` | Template for the API key |
| `requirements.txt` | Python packages |

---

## How the GUI is structured

The window is a **frontend only**. After you search:

1. It calls `WeatherService.get_bundle(city)`.
2. It downloads weather icons in a background thread so the window does not freeze.
3. It draws:
   - large current temperature and place name
   - hourly strip (6 hours)
   - five-day list
   - UV / humidity / wind / sun tiles

The °C button switches units using data already on screen.

---

## Errors you might see

| Message | Meaning |
|---------|---------|
| Enter a city name or ZIP code | Search box was empty |
| No weather found for "…" | Spelling / unknown place |
| The OpenWeatherMap API key is invalid | Check `.env` (or wait if the key is new) |
| Timed out / could not reach | Network problem |

---

## Assignment notes

- **Beginner:** CLI + `WeatherService`
- **Advanced:** GUI with current + hourly + daily + icons + unit toggle
- **Bonus:** IP-based city detect
- Frontends never import `requests` except the backend module
