# METAR Weather App

A Flask web application that fetches and displays **METAR** (Meteorological Aerodrome Report) weather data for airports worldwide. METAR is the international standard format used by meteorologists and aviation professionals to communicate current weather conditions at airports.

---

## What is METAR?

METAR is a standardised weather observation format used in aviation. Each report is issued by airports (usually every 30 or 60 minutes) and includes:

| Field | Description |
|---|---|
| Station ID | 4-letter ICAO airport code |
| Observation Time | UTC date and time |
| Wind | Direction (degrees) and speed (knots), with optional gusts |
| Visibility | In statute miles or metres |
| Sky Condition | Cloud layers (FEW / SCT / BKN / OVC) with altitude in hundreds of feet |
| Temperature & Dewpoint | In degrees Celsius |
| Altimeter Setting | Atmospheric pressure in inHg or hPa |
| Present Weather | Rain, snow, fog, thunderstorm, etc. |

**Example raw METAR:**
```
KJFK 151856Z 28015KT 10SM BKN250 M01/M15 A3040 RMK AO2 SLP288
```

---

## Features

- Search any airport by its **ICAO code** (e.g. `KJFK`, `EGLL`, `VIDP`)
- Displays all METAR fields in a clean, readable dashboard
- **Flight category** badge — VFR / MVFR / IFR / LIFR
- Temperature in both **°C and °F**
- Wind speed in both **knots and mph**
- Visibility in **statute miles and metres**
- Pressure in both **inHg and hPa**
- Sky condition decoding with ceiling altitude
- JSON REST API endpoint for programmatic access
- Responsive UI with Bootstrap 5
- Quick links for 8 popular international airports

---

## Project Structure

```
metar-app/
├── app.py                  # Flask application (routes, parsing, fetch logic)
├── requirements.txt        # Python dependencies
├── .gitignore              # Files excluded from git
├── README.md               # This file
├── templates/
│   ├── base.html           # Shared layout (navbar, footer)
│   ├── index.html          # Home / search page
│   ├── metar.html          # METAR result page
│   └── error.html          # Error page
└── static/
    ├── css/
    │   └── style.css       # Custom styles
    └── js/
        └── main.js         # Input auto-uppercase handling
```

---

## Prerequisites

- Python 3.9 or higher
- pip (comes with Python)
- Internet connection (data is fetched live from NOAA)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/metar-app.git
cd metar-app
```

### 2. Create and activate a virtual environment

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

You will see `(venv)` at the start of your terminal prompt when the environment is active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## Usage

### Web Interface

1. Open **http://localhost:5000**
2. Enter a 4-letter ICAO airport code in the search box (e.g. `KJFK`)
3. Click **Get METAR** to view the weather report

Or click any of the quick-access popular airport buttons on the home page.

### REST API

The app also exposes a JSON API:

```
GET /api/metar/<ICAO>
```

**Example:**
```bash
curl http://localhost:5000/api/metar/KJFK
```

**Example response:**
```json
{
  "status": "ok",
  "data": {
    "raw": "KJFK 151856Z 28015KT 10SM BKN250 M01/M15 A3040 RMK AO2",
    "station_id": "KJFK",
    "observation_time": "2025-01-15 18:56 UTC",
    "temperature_c": -1.0,
    "temperature_f": 30.2,
    "dewpoint_c": -15.0,
    "dewpoint_f": 5.0,
    "wind_direction_deg": 280,
    "wind_speed_kt": 15,
    "wind_speed_mph": 17.3,
    "wind_gust_kt": null,
    "wind_gust_mph": null,
    "visibility_sm": 10.0,
    "visibility_m": 16093,
    "sky_condition": ["BKN250"],
    "ceiling_ft": 25000,
    "present_weather": "",
    "pressure_inhg": 30.4,
    "pressure_hpa": 1029.5,
    "flight_category": "VFR",
    "flight_color": "success"
  }
}
```

---

## Flight Categories

| Category | Ceiling | Visibility | Colour |
|---|---|---|---|
| **VFR** – Visual Flight Rules | > 3000 ft | > 5 SM | Green |
| **MVFR** – Marginal VFR | 1000–3000 ft | 3–5 SM | Blue |
| **IFR** – Instrument Flight Rules | 500–999 ft | 1–3 SM | Yellow |
| **LIFR** – Low IFR | < 500 ft | < 1 SM | Red |

---

## ICAO Code Reference

Some commonly used ICAO codes:

| ICAO | Airport |
|---|---|
| KJFK | New York John F. Kennedy |
| KLAX | Los Angeles International |
| EGLL | London Heathrow |
| LFPG | Paris Charles de Gaulle |
| EDDF | Frankfurt International |
| VIDP | Delhi Indira Gandhi |
| OMDB | Dubai International |
| YSSY | Sydney Kingsford Smith |
| RJTT | Tokyo Haneda |
| ZBAA | Beijing Capital |

---

## Data Source

Live METAR data is fetched from the **NOAA (National Oceanic and Atmospheric Administration)** public server:

```
https://tgftp.nws.noaa.gov/data/observations/metar/stations/{ICAO}.TXT
```

---

## Deactivating the Virtual Environment

When you're done:

```bash
deactivate
```

---

## License

MIT License. Free to use, modify, and distribute.
