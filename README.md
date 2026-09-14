# OIBSIP

Oasis Infobyte Internship Program — Python tasks in one repository.

**Team**
- Owner: you
- Collaborator: Lentswe (same internship, same repo)

| Task | Folder |
|------|--------|
| Weather App | `weather_app/` |
| Voice assistant | `voice_assistant/` |
| BMI calculator | `bmi_calculator/` |

---

## Weather App

Looks up weather for a city or ZIP code.

- Current temperature (°C and °F), humidity, condition, wind
- Weather icons
- Next 6 hours and next 5 days
- °C / °F toggle (does not call the API again)
- Errors shown in the GUI (empty input, city not found, timeout, bad key)
- Optional city pre-fill from ipinfo.io (if that fails, the field stays empty)

**Files**
- `weather_app/weather_service.py` — backend (OpenWeatherMap). Both UIs call this.
- `weather_app/weather_cli.py` — terminal
- `weather_app/weather_gui.py` — window (title: OIBSIP Weather App)

The CLI and GUI do not call the API themselves. All HTTP and JSON parsing lives in `weather_service.py`.

### Setup
``bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

