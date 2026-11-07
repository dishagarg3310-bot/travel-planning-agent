"""Places discovery tool for the travel planning agent."""
import json
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "places.json"


def load_places() -> list:
    """Load all places from places.json."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Error loading places: {error}")
        return []


@tool
def discover_places(
    city: str,
    place_type: Optional[str] = None,
    min_rating: float = 0.0,
    limit: int = 6,
) -> str:
    """Find attractions in a city, sorted by highest rating.

    Args:
        city: City name, e.g. 'Goa'.
        place_type: Optional type: beach, fort, lake, market, monument,
            museum, park or temple.
        min_rating: Minimum rating (0 to 5).
        limit: Maximum number of places to return.

    Returns:
        JSON string with the list of recommended places.
    """
    places = load_places()
    matches = [
        place for place in places
        if place["city"].lower() == city.strip().lower()
        and place["rating"] >= min_rating
        and (place_type is None or place["type"].lower() == place_type.strip().lower())
    ]

    if not matches:
        return json.dumps({"error": f"No places found in {city} for the given filters"})

    matches.sort(key=lambda place: place["rating"], reverse=True)
    return json.dumps({"count": len(matches[:limit]), "places": matches[:limit]})