"""Budget estimation tool for the travel planning agent."""
import json

from langchain_core.tools import tool


@tool
def estimate_budget(
    onward_flight_price: float,
    hotel_price_per_night: float,
    num_nights: int,
    return_flight_price: float = 0.0,
    local_expense_per_day: float = 800.0,
    num_days: int = 0,
) -> str:
    """Estimate the total trip budget in INR.

    Pass plain numbers only (never expressions like 100+200).

    Args:
        onward_flight_price: Onward flight price in INR.
        hotel_price_per_night: Hotel price per night in INR.
        num_nights: Number of hotel nights.
        return_flight_price: Return flight price in INR (0 if not available).
        local_expense_per_day: Food and local travel cost per day in INR.
        num_days: Number of trip days. If 0, num_nights + 1 is used.

    Returns:
        JSON string with the cost breakdown and total.
    """
    if min(onward_flight_price, return_flight_price, hotel_price_per_night, num_nights) < 0:
        return json.dumps({"error": "Prices and nights cannot be negative"})

    days = num_days if num_days > 0 else num_nights + 1
    flight_total = onward_flight_price + return_flight_price
    hotel_total = hotel_price_per_night * num_nights
    local_total = local_expense_per_day * days
    total = flight_total + hotel_total + local_total

    return json.dumps({
        "flight": flight_total,
        "hotel": hotel_total,
        "food_and_local_travel": local_total,
        "total": total,
        "currency": "INR",
    })