"""Flight search tool for the travel planning agent."""
import json
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "flights.json"


def load_flights() -> list:
    """Load all flights from flights.json."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Error loading flights: {error}")
        return []


def _duration_minutes(flight: dict) -> float:
    """Return flight duration in minutes."""
    departure = datetime.fromisoformat(flight["departure_time"])
    arrival = datetime.fromisoformat(flight["arrival_time"])
    return (arrival - departure).total_seconds() / 60


@tool
def search_flights(source: str, destination: str, preference: str = "cheapest") -> str:
    """Search flights between two cities.

    Args:
        source: Departure city, e.g. 'Delhi'.
        destination: Arrival city, e.g. 'Goa'.
        preference: 'cheapest' or 'fastest'.

    Returns:
        JSON string with the best flight and up to 3 options.
    """
    flights = load_flights()
    matches = [
        flight for flight in flights
        if flight["from"].lower() == source.strip().lower()
        and flight["to"].lower() == destination.strip().lower()
    ]

    if not matches:
        return json.dumps({"error": f"No flights found from {source} to {destination}"})

    if preference.strip().lower() == "fastest":
        matches.sort(key=_duration_minutes)
    else:
        matches.sort(key=lambda flight: flight["price"])

    return json.dumps({
        "preference_used": preference,
        "best_option": matches[0],
        "all_options": matches[:3],
    })