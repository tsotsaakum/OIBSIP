# OIBSIP

Oasis Infobyte Internship Program — three Python tasks in **one** GitHub repo.

**Team:** you (owner) 
Clone **once**, then go into the folder for the task you want:

```bash
git clone https://github.com/YOUR_USERNAME/OIBSIP.git
cd OIBSIP
```

| # | Project | Go into this folder | Needs `.env` / API key? |
|---|---------|---------------------|-------------------------|
| 1 | Weather App | `weather_app/` (run from repo **root**) | Yes — OpenWeatherMap (optional; demo works without it) |
| 2 | Voice assistant | `voice_assistant/` | Only if *that* project uses an API |
| 3 | BMI calculator | `bmi_calculator/` | No |

Do **not** mix their install commands. Each project has its own setup below.

---

## 1. Weather App

**What it is:** city or ZIP → temperature, humidity, condition, wind, icons, next 6 hours, next 5 days, °C/°F toggle.

**Where the code is:** `weather_app/`  
Run these commands from the **repo root** (`OIBSIP/`), not from inside `voice_assistant` or `bmi_calculator`.

### Weather App — setup

```bash
cd OIBSIP
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Mac/Linux activate: `source venv/bin/activate`

Ubuntu if Tkinter is missing: `sudo apt-get install python3-tk`

Edit **only** `.env` for this project:

```
OPENWEATHERMAP_API_KEY=your_key_here
```

Leave it blank for demo weather. Do not commit `.env`.

### Weather App — run

```bash
python -m weather_app
python -m weather_app --city London
python -m weather_app --cli --loop
python -m pytest -q
```

Window title: **OIBSIP Weather App**.

---

## 2. Voice assistant

**What it is:** microphone → command → spoken reply (your OIBSIP voice task).

**Where the code is:** `voice_assistant/`  
This is **not** the weather app. Do not use `python -m weather_app` here.

### Voice assistant — setup

```bash
cd OIBSIP/voice_assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

If this folder has no `requirements.txt` yet, add one for *this* project only (for example `SpeechRecognition`, `pyttsx3`). Do **not** copy the weather `.env` here unless the voice app needs its own key.

### Voice assistant — run

```bash
python main.py
```

Change `main.py` to whatever filename you actually use. Write the exact command in `voice_assistant/README.md` when you add the files.

---

## 3. BMI calculator

**What it is:** height + weight → BMI number and category.

**Where the code is:** `bmi_calculator/`  
This is **not** the weather app and **not** the voice assistant.

### BMI calculator — setup

```bash
cd OIBSIP/bmi_calculator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

If it is a single script with no extra packages:

```bash
cd OIBSIP/bmi_calculator
python bmi.py
```

No OpenWeatherMap key. No microphone. Only height and weight.

### BMI calculator — run

```bash
python bmi.py
```

Rename `bmi.py` to your real filename and put that in `bmi_calculator/README.md`.

---

## Quick “which command?” 

| I want to… | Folder | Command |
|------------|--------|---------|
| See the weather window | repo root `OIBSIP/` | `python -m weather_app` |
| Talk to the assistant | `voice_assistant/` | `python main.py` |
| Calculate BMI | `bmi_calculator/` | `python bmi.py` |

If something fails, check you `cd`’d into the **correct** project first.

