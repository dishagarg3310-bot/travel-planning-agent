"""LangChain tool-calling agent that builds travel itineraries."""
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from tools.budget_tool import estimate_budget
from tools.flight_tool import search_flights
from tools.hotel_tool import recommend_hotels
from tools.places_tool import discover_places
from tools.weather_tool import get_weather

load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are an expert AI travel planner for Indian travellers.

Always use the tools to get real data. Never invent flights, hotels or places.
Only put attractions returned by discover_places in the itinerary. Do not add
outside places or restaurants.

Workflow:
1. Call search_flights for the onward route (user's preference: cheapest or fastest).
2. Call search_flights again for the return route (destination to source).
3. Call recommend_hotels for the destination city.
4. Call get_weather for the destination with the trip dates (YYYY-MM-DD).
5. Call discover_places for the destination city with limit 10 and no place_type,
   so that you can see every type of place.
6. Call estimate_budget with onward_flight_price, return_flight_price
   (0 if no return flight), hotel_price_per_night, num_nights and num_days.
   Pass plain numbers only. Never pass expressions like 100+200.

Weather-aware itinerary rules:
- Indoor types: museum, market, temple. Outdoor types: beach, park, lake, fort, monument.
- On a day with rain, drizzle, thunderstorm or fog, prefer indoor places.
  On other days prefer outdoor places. If max temperature is 38 C or more,
  include one indoor place for the afternoon.
- Plan 2 places per day. If the city has fewer than 2 places per day in total,
  spread ALL available places across the days so that no day is empty.
- If the preferred type runs out, fill the day with any remaining place and
  mention this in the reason. Never repeat a place.
- The place names in the data are generic, so the type matters. Write every
  place in the itinerary as "Place Name (type)", for example
  "Famous Park (museum)", using the type returned by discover_places.
- Give every day a short reason that mentions that day's weather and the
  type of places chosen.
  
Important rules:
- Flight dates in the dataset are fixed and may not match the trip dates.
  Do NOT mention the date mismatch; just use the route, airline and price.
- If no flight exists for a route, clearly say so, but STILL complete hotel,
  places, weather and budget. Use 0 for the missing flight prices in estimate_budget.
- If a tool returns an error, say so clearly instead of making things up.

Final answer format:
## Trip Summary
## Flight Selected (onward and return)
## Hotel Recommendation
## Weather (day-wise)
## Day-wise Itinerary
## Budget Breakdown
## Why we selected this
## JSON Output
Under "JSON Output" give ONE json code block (and nothing after it) with exactly
these keys: trip_summary (source, destination, start_date, end_date, num_days),
flight (onward and return, each with airline, flight_id, price),
hotel (name, stars, price_per_night, nights), weather (list of date,
max_temp_c, min_temp_c, condition), itinerary (list of day, date, places, reason),
budget (flight, hotel, food_and_local_travel, total), reasoning (list of strings).
Use plain numbers, never expressions. The JSON must be valid.
Keep the answer clear and well structured. All prices are in INR (Rs)."""

def build_agent():
    """Create the travel planning agent with all tools attached."""
    model = ChatGroq(model=MODEL_NAME, temperature=0, max_retries=8, timeout=120)
    tools = [
        search_flights,
        recommend_hotels,
        discover_places,
        get_weather,
        estimate_budget,
    ]
    return create_agent(model, tools, system_prompt=SYSTEM_PROMPT)


def plan_trip(user_query: str) -> str:
    """Run the agent on a user query and return the final itinerary text."""
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    return result["messages"][-1].content

def plan_trip_with_steps(user_query: str):
    """Run the agent and return (final answer, list of tool-call steps)."""
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    messages = result["messages"]

    calls = {}
    steps = []
    for message in messages:
        for call in getattr(message, "tool_calls", None) or []:
            calls[call["id"]] = call
        if message.type == "tool":
            call = calls.get(message.tool_call_id, {})
            steps.append({
                "tool": message.name,
                "input": call.get("args", {}),
                "output": message.content,
            })
    return messages[-1].content, steps

if __name__ == "__main__":
    query = (
        "Plan a 3-day trip from Hyderabad to Delhi from 2026-11-12 to 2026-11-14. "
        "I want the cheapest flight and a 4-star or better hotel."
    )
    print(plan_trip(query))