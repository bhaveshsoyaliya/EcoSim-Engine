import requests

TIMEOUT = 10  # seconds

def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}

    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()

        if "results" not in data:
            return None

        p = data["results"][0]
        return p["latitude"], p["longitude"]

    except requests.exceptions.RequestException:
        return None


def get_live_environment(city):
    coords = get_coordinates(city)

    if coords is None:
        return None

    lat, lon = coords

    air_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&current=pm2_5,pm10,nitrogen_dioxide,ozone"
    )

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
    )

    try:
        air = requests.get(air_url, timeout=TIMEOUT)
        weather = requests.get(weather_url, timeout=TIMEOUT)

        air.raise_for_status()
        weather.raise_for_status()

        air = air.json()
        weather = weather.json()

        a = air.get("current", {})
        w = weather.get("current", {})

        return {
            "lat": lat,
            "lon": lon,
            "pm25": a.get("pm2_5", 0) or 0,
            "pm10": a.get("pm10", 0) or 0,
            "no2": a.get("nitrogen_dioxide", 0) or 0,
            "o3": a.get("ozone", 0) or 0,
            "temperature": w.get("temperature_2m", 0) or 0,
            "humidity": w.get("relative_humidity_2m", 0) or 0,
            "wind": w.get("wind_speed_10m", 0) or 0,
            "rain": w.get("precipitation", 0) or 0,
        }

    except requests.exceptions.RequestException:
        # Fallback demo values
        return {
            "lat": lat,
            "lon": lon,
            "pm25": 18.5,
            "pm10": 32.1,
            "no2": 14.2,
            "o3": 52.8,
            "temperature": 29.4,
            "humidity": 61,
            "wind": 11.3,
            "rain": 0.0,
        }