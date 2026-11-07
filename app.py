"""Streamlit interface for the Agentic AI Travel Planning Assistant."""
import json
import re
from datetime import date, timedelta

import streamlit as st

from agent.travel_agent import plan_trip

CITIES = ["Bangalore", "Chennai", "Delhi", "Goa", "Hyderabad", "Jaipur", "Kolkata", "Mumbai"]


def split_itinerary(text: str):
    """Split the agent answer into readable text and the JSON block (if valid)."""
    match = re.search(r"```json\s*(\{.*\})\s*```", text, re.DOTALL)
    if not match:
        return text, None
    readable = text[: match.start()].replace("## JSON Output", "").rstrip()
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        data = None
    return readable, data


st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="centered")
st.title("✈️ Agentic AI Travel Planner")
st.caption("Flights, hotels, places and live weather, planned by an AI agent.")

with st.sidebar:
    st.header("Trip details")
    source = st.selectbox("From", CITIES, index=CITIES.index("Hyderabad"))
    destination = st.selectbox("To", CITIES, index=CITIES.index("Goa"))
    start_date = st.date_input("Start date", value=date.today() + timedelta(days=3))
    end_date = st.date_input("End date", value=date.today() + timedelta(days=5))
    flight_preference = st.radio("Flight preference", ["cheapest", "fastest"])
    min_stars = st.slider("Minimum hotel stars", 1, 5, 4)
    extra_notes = st.text_input("Extra preferences (optional)", placeholder="e.g. love beaches")
    generate = st.button("Plan my trip", type="primary")

if generate:
    num_days = (end_date - start_date).days + 1
    if source == destination:
        st.error("Source and destination cannot be the same.")
    elif end_date < start_date:
        st.error("End date must be after the start date.")
    elif not 3 <= num_days <= 7:
        st.error("Please choose a trip of 3 to 7 days.")
    else:
        query = (
            f"Plan a {num_days}-day trip from {source} to {destination} "
            f"from {start_date} to {end_date}. "
            f"I want the {flight_preference} flight and a hotel with at least "
            f"{min_stars} stars. {extra_notes}"
        )
        with st.spinner("Agent is planning your trip..."):
            try:
                answer = plan_trip(query)
                readable, trip_json = split_itinerary(answer)
                st.markdown(readable)
                if trip_json:
                    st.subheader("JSON Output")
                    st.json(trip_json, expanded=False)
                    st.download_button(
                        "Download itinerary (JSON)",
                        data=json.dumps(trip_json, indent=2),
                        file_name=f"trip_{source}_{destination}.json",
                        mime="application/json",
                    )
            except Exception as error:
                st.error(f"Something went wrong: {error}")
else:
    st.info("Fill in the trip details in the sidebar and click 'Plan my trip'.")