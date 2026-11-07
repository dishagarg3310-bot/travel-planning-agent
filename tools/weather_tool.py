"""Weather lookup tool using the free Open-Meteo API."""
import json

import requests
from langchain_core.tools import tool

API_URL = "https://api.open-meteo.com/v1/forecast"

CITY_COORDINATES = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "kolkata": (22.5726, 88.3639),
    "jaipur": (26.9124, 75.7873),
    "goa": (15.2993, 74.1240),
}

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog", 51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 80: "Rain showers",
    81: "Rain showers", 82: "Heavy rain showers", 95: "Thunderstorm",
}


@tool
def get_weather(city: str, start_date: str, end_date: str) -> str:
    """Get day-wise weather forecast for a city.

    Args:
        city: City name, e.g. 'Goa'.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        JSON string with daily max/min temperature and conditions.
        Forecast works only for dates within the next ~16 days.
    """
    coordinates = CITY_COORDINATES.get(city.strip().lower())
    if coordinates is None:
        return json.dumps({"error": f"No coordinates available for {city}"})

    params = {
        "latitude": coordinates[0],
        "longitude": coordinates[1],
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        daily = response.json()["daily"]
    except (requests.RequestException, KeyError, ValueError) as error:
        return json.dumps({"error": f"Weather lookup failed: {error}"})

    forecast = []
    for index, date in enumerate(daily["time"]):
        forecast.append({
            "date": date,
            "max_temp_c": daily["temperature_2m_max"][index],
            "min_temp_c": daily["temperature_2m_min"][index],
            "condition": WEATHER_CODES.get(daily["weathercode"][index], "Unknown"),
        })

    return json.dumps({"city": city, "forecast": forecast})