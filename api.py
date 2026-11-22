"""FastAPI backend: serves the website, the trip planning API and trip history."""
import json
import re
from datetime import date

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.travel_agent import plan_trip_with_steps
from database import delete_trip, get_trip, init_db, list_trips, save_trip
from pdf_export import build_trip_pdf

app = FastAPI(title="AI Travel Planner")
init_db()


class TripRequest(BaseModel):
    """Data sent by the website form."""

    source: str
    destination: str
    start_date: date
    end_date: date
    flight_preference: str = "cheapest"
    min_stars: int = 4
    extra_notes: str = ""


def split_itinerary(text: str):
    """Split the agent answer into readable text and the JSON block."""
    match = re.search(r"```json\s*(\{.*\})\s*```", text, re.DOTALL)
    if not match:
        return text, None
    readable = text[: match.start()].replace("## JSON Output", "").rstrip()
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        data = None
    return readable, data


@app.post("/api/plan")
def plan(request: TripRequest):
    """Run the travel agent, save the trip and return everything."""
    num_days = (request.end_date - request.start_date).days + 1
    if request.source == request.destination:
        raise HTTPException(400, "Source and destination cannot be the same.")
    if not 3 <= num_days <= 7:
        raise HTTPException(400, "Please choose a trip of 3 to 7 days.")

    query = (
        f"Plan a {num_days}-day trip from {request.source} to {request.destination} "
        f"from {request.start_date} to {request.end_date}. "
        f"I want the {request.flight_preference} flight and a hotel with at least "
        f"{request.min_stars} stars. {request.extra_notes}"
    )
    try:
        answer, steps = plan_trip_with_steps(query)
    except Exception as error:
        raise HTTPException(500, f"Agent failed: {error}")

    readable, trip_json = split_itinerary(answer)

    trip_id = None
    if trip_json:
        try:
            trip_id = save_trip(
                request.source,
                request.destination,
                str(request.start_date),
                str(request.end_date),
                num_days,
                request.flight_preference,
                trip_json,
                readable,
            )
        except Exception as error:
            print(f"Could not save trip: {error}")

    return {"readable": readable, "trip": trip_json, "steps": steps, "trip_id": trip_id}


@app.get("/api/trips")
def trips():
    """Return the recent saved trips."""
    return list_trips()


@app.get("/api/trips/{trip_id}")
def trip_detail(trip_id: int):
    """Return one saved trip."""
    data = get_trip(trip_id)
    if data is None:
        raise HTTPException(404, "Trip not found.")
    return data


@app.delete("/api/trips/{trip_id}")
def trip_delete(trip_id: int):
    """Delete one saved trip."""
    if not delete_trip(trip_id):
        raise HTTPException(404, "Trip not found.")
    return {"deleted": trip_id}


@app.post("/api/pdf")
def pdf(trip: dict):
    """Create a PDF from the trip JSON."""
    return Response(content=build_trip_pdf(trip), media_type="application/pdf")


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    """Serve the website home page."""
    return FileResponse("static/index.html")