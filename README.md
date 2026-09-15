# OIBSIP

Oasis Infobyte internship — two Python tasks in **one** GitHub repo.

| # | Project | Folder | Run from |
|---|---------|--------|----------|
| 1 | Weather app (Lentswe) | `weather_app/` | `weather_app/` |
| 2 | Voice assistant (Lentswe) | `voice_assistant/` | `voice_assistant/` |

Each folder has its own `requirements.txt` and `.env.example`. Do not mix their virtualenvs.

```text
git clone https://github.com/tsotsaakum/OIBSIP.git
cd OIBSIP
```

---

## 1. Weather app

City or ZIP → temperature, humidity, conditions, wind, pressure, sunrise and sunset, next 6 hours, next 5 days. Web dashboard, Tkinter GUI, and CLI.

### Setup

```text
cd weather_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with a free [OpenWeatherMap](https://home.openweathermap.org/api_keys) key, or leave it blank for demo weather. Do not commit `.env`.

### Run

```text
python weather_gui.py
python weather_cli.py
python web/serve.py
```

Web preview: http://127.0.0.1:8080

More detail: [`weather_app/README.md`](weather_app/README.md)

---

## 2. Voice assistant

Speak or type in South Africa’s 11 official languages. Browser mic, spoken replies, optional Groq chat.

### Setup

```text
cd voice_assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

`.env` is optional. Groq / SMTP / OpenRouteService keys are only needed for those extras.

### Run

```text
python app.py
```

Open http://127.0.0.1:7000

More detail: [`voice_assistant/README.md`](voice_assistant/README.md)
