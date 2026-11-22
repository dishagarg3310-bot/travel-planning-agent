# WanderAI: Agentic AI Travel Planning Assistant (LangChain)

An AI travel agent that understands a trip request, calls tools on its own and
produces a complete itinerary: flights, hotel, day-wise weather, places and
budget. Results are shown on a website and also available as JSON and PDF.

## Problem Statement
Planning a trip means switching between many websites for flights, hotels,
attractions and weather. This project automates that with a LangChain
tool-calling agent that reasons step by step and builds an optimized itinerary.

## Features
- Flight search (cheapest or fastest), onward and return, from `flights.json`
- Hotel recommendation filtered by city, stars and price from `hotels.json`
- Places discovery by city, type and rating from `places.json`
- Live day-wise weather from the free Open-Meteo API (no API key needed)
- Budget estimation (flights + hotel + daily local expenses)
- Weather-aware itinerary: indoor places on rainy or foggy days, outdoor places on clear days
- Reasoning for every day and for every choice ("Why we selected this")
- Agent steps view: see which tools the agent called, with inputs and outputs
- Output as readable text, clean JSON and downloadable PDF
- Trip history saved in a SQLite database (open or delete old trips)
- Website (FastAPI + HTML/CSS/JS) and a simple Streamlit interface

## Tech Stack
Python, LangChain, Groq LLM (`openai/gpt-oss-120b`), Open-Meteo API, FastAPI,
SQLite, HTML/CSS/JavaScript, Streamlit, fpdf2

## Project Structure
```
travel-planning-agent/
├── data/              # flights.json, hotels.json, places.json
├── tools/             # flight, hotel, places, weather, budget tools
├── agent/             # LangChain agent and system prompt
├── static/            # website: index.html, style.css, script.js
├── api.py             # FastAPI backend (website + API)
├── database.py        # SQLite trip history
├── pdf_export.py      # PDF generation
├── app.py             # Streamlit interface (alternative UI)
├── requirements.txt
└── README.md
```

## Setup
1. Clone the repository and open the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Get a free API key from https://console.groq.com and create a `.env` file:
   ```
   GROQ_API_KEY=your_key_here
   ```

## Run
Website (main):
```
uvicorn api:app --reload
```
Open http://127.0.0.1:8000

Streamlit version (optional):
```
streamlit run app.py
```

## API Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/plan` | Plan a trip with the agent and save it |
| GET | `/api/trips` | List recent saved trips |
| GET | `/api/trips/{id}` | Open one saved trip |
| DELETE | `/api/trips/{id}` | Delete a saved trip |
| POST | `/api/pdf` | Create a PDF from trip JSON |

## Agent Tools
| Tool | What it does |
|---|---|
| `search_flights` | Filters flights by route, returns cheapest or fastest |
| `recommend_hotels` | Filters hotels by city, stars and price |
| `discover_places` | Lists attractions by city, type and rating |
| `get_weather` | Gets the forecast from Open-Meteo |
| `estimate_budget` | Adds flights, hotel nights and daily local expenses |

## How It Works
1. The user fills the form (cities, dates, flight preference, hotel stars).
2. The agent calls the tools: flights (onward and return), hotels, weather, places, budget.
3. It builds a day-wise itinerary using only data returned by the tools, choosing
   indoor or outdoor places based on each day's weather.
4. The backend splits the answer into readable text and JSON, saves it in SQLite
   and sends everything to the website.

## Database
SQLite file `trips.db` (created automatically, not committed to Git) with a
`trips` table: trip_id, source_city, destination_city, start_date, end_date,
num_days, flight_preference, total_budget, trip_json, readable_text, created_at.
An index on `created_at` speeds up the history list.

## Notes
- The datasets are sample data: flight dates and place names are synthetic, and
  not every route has a flight. The agent says so and still completes the plan.
- Weather forecast works only for dates within the next ~16 days.
- Cities supported: Bangalore, Chennai, Delhi, Goa, Hyderabad, Jaipur, Kolkata, Mumbai.
- Groq's free tier has a tokens-per-minute limit; the agent retries automatically.