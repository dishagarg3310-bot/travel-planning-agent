"""Hotel recommendation tool for the travel planning agent."""
import json
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "hotels.json"


def load_hotels() -> list:
    """Load all hotels from hotels.json."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Error loading hotels: {error}")
        return []


@tool
def recommend_hotels(
    city: str,
    min_stars: int = 1,
    max_price_per_night: Optional[int] = None,
    sort_by: str = "stars",
) -> str:
    """Recommend hotels in a city.

    Args:
        city: City name, e.g. 'Goa'.
        min_stars: Minimum star rating (1 to 5).
        max_price_per_night: Maximum price per night in INR (optional).
        sort_by: 'stars' for highest rated, 'price' for cheapest.

    Returns:
        JSON string with the best hotel and up to 3 options.
    """
    hotels = load_hotels()
    matches = [
        hotel for hotel in hotels
        if hotel["city"].lower() == city.strip().lower()
        and hotel["stars"] >= min_stars
        and (max_price_per_night is None or hotel["price_per_night"] <= max_price_per_night)
    ]

    if not matches:
        return json.dumps({"error": f"No hotels found in {city} for the given filters"})

    if sort_by.strip().lower() == "price":
        matches.sort(key=lambda hotel: hotel["price_per_night"])
    else:
        matches.sort(key=lambda hotel: (-hotel["stars"], hotel["price_per_night"]))

    return json.dumps({
        "sort_used": sort_by,
        "best_option": matches[0],
        "all_options": matches[:3],
    })