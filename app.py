from flask import Flask, render_template, jsonify, request, abort
import requests
from metar import Metar as MetarParser

app = Flask(__name__)

NOAA_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT"

WEATHER_DESCRIPTIONS = {
    "RA": "Rain", "SN": "Snow", "DZ": "Drizzle", "GR": "Hail",
    "GS": "Small Hail", "TS": "Thunderstorm", "FG": "Fog",
    "BR": "Mist", "HZ": "Haze", "FU": "Smoke", "SA": "Sand",
    "DU": "Dust", "SQ": "Squall", "FC": "Funnel Cloud",
    "SS": "Sandstorm", "DS": "Duststorm", "PL": "Ice Pellets",
    "IC": "Ice Crystals", "UP": "Unknown Precipitation",
}

INTENSITY_LABELS = {"-": "Light", "": "Moderate", "+": "Heavy", "VC": "In Vicinity"}


def fetch_raw_metar(icao: str) -> str:
    icao = icao.strip().upper()
    url = NOAA_URL.format(icao=icao)
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    lines = [l.strip() for l in response.text.strip().splitlines() if l.strip()]
    # NOAA file: line 0 = observation timestamp, line 1 = raw METAR
    if len(lines) < 2:
        raise ValueError("Unexpected NOAA response format")
    return lines[1]


def calculate_flight_rules(ceiling_ft, visibility_sm):
    if ceiling_ft is None and visibility_sm is None:
        return "VFR", "success"
    c = ceiling_ft if ceiling_ft is not None else 99999
    v = visibility_sm if visibility_sm is not None else 99999
    if c < 500 or v < 1:
        return "LIFR", "danger"
    if c < 1000 or v < 3:
        return "IFR", "warning"
    if c <= 3000 or v <= 5:
        return "MVFR", "info"
    return "VFR", "success"


def format_sky_layer(layer):
    cover, height, modifier = layer
    if height:
        try:
            height_ft = int(height.value("FT"))
            code = f"{cover}{height_ft // 100:03d}"
        except Exception:
            code = cover
    else:
        code = cover
    if modifier:
        code += f" ({modifier})"
    return code


def get_ceiling(sky_layers):
    for layer in sky_layers:
        cover, height, _ = layer
        if cover in ("BKN", "OVC") and height:
            try:
                return int(height.value("FT"))
            except Exception:
                pass
    return None


def parse_metar(raw: str) -> dict:
    obs = MetarParser.Metar(raw)

    temp_c = obs.temp.value() if obs.temp else None
    dewpt_c = obs.dewpt.value() if obs.dewpt else None
    temp_f = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None
    dewpt_f = round(dewpt_c * 9 / 5 + 32, 1) if dewpt_c is not None else None

    wind_kt = obs.wind_speed.value() if obs.wind_speed else None
    wind_mph = round(wind_kt * 1.15078, 1) if wind_kt is not None else None
    wind_dir = obs.wind_dir.value() if obs.wind_dir else None
    wind_gust_kt = obs.wind_gust.value() if obs.wind_gust else None
    wind_gust_mph = round(wind_gust_kt * 1.15078, 1) if wind_gust_kt is not None else None

    visibility_sm = obs.vis.value("SM") if obs.vis else None
    visibility_m = obs.vis.value("M") if obs.vis else None

    pressure_inhg = obs.press.value("IN") if obs.press else None
    pressure_hpa = obs.press.value("MB") if obs.press else None

    sky_layers = obs.sky if obs.sky else []
    sky_str = [format_sky_layer(layer) for layer in sky_layers]
    ceiling_ft = get_ceiling(sky_layers)

    flight_category, flight_color = calculate_flight_rules(ceiling_ft, visibility_sm)

    weather_str = obs.present_weather() if hasattr(obs, "present_weather") else ""

    return {
        "raw": raw,
        "station_id": obs.station_id,
        "observation_time": obs.time.strftime("%Y-%m-%d %H:%M UTC") if obs.time else None,
        "temperature_c": round(temp_c, 1) if temp_c is not None else None,
        "temperature_f": temp_f,
        "dewpoint_c": round(dewpt_c, 1) if dewpt_c is not None else None,
        "dewpoint_f": dewpt_f,
        "wind_direction_deg": wind_dir,
        "wind_speed_kt": wind_kt,
        "wind_speed_mph": wind_mph,
        "wind_gust_kt": wind_gust_kt,
        "wind_gust_mph": wind_gust_mph,
        "visibility_sm": round(visibility_sm, 2) if visibility_sm is not None else None,
        "visibility_m": round(visibility_m) if visibility_m is not None else None,
        "sky_condition": sky_str,
        "ceiling_ft": ceiling_ft,
        "present_weather": weather_str,
        "pressure_inhg": round(pressure_inhg, 2) if pressure_inhg is not None else None,
        "pressure_hpa": round(pressure_hpa, 1) if pressure_hpa is not None else None,
        "flight_category": flight_category,
        "flight_color": flight_color,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/metar/<icao>")
def metar_page(icao):
    try:
        raw = fetch_raw_metar(icao)
        data = parse_metar(raw)
        return render_template("metar.html", data=data, icao=icao.upper())
    except requests.HTTPError as e:
        error = f"Airport '{icao.upper()}' not found or METAR unavailable."
        return render_template("error.html", error=error, icao=icao.upper()), 404
    except Exception as e:
        return render_template("error.html", error=str(e), icao=icao.upper()), 500


@app.route("/api/metar/<icao>")
def api_metar(icao):
    try:
        raw = fetch_raw_metar(icao)
        data = parse_metar(raw)
        return jsonify({"status": "ok", "data": data})
    except requests.HTTPError as e:
        return jsonify({"status": "error", "message": f"Airport '{icao.upper()}' not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/search")
def search():
    icao = request.args.get("icao", "").strip().upper()
    if not icao:
        return render_template("index.html", error="Please enter an ICAO code.")
    if len(icao) != 4 or not icao.isalpha():
        return render_template("index.html", error="ICAO codes are 4 letters (e.g. KJFK, EGLL, VIDP).")
    return metar_page(icao)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
