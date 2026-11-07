# Agentic AI-Based Travel Planning Assistant (LangChain)

An AI travel agent that understands a trip request, calls tools on its own, and
produces a complete itinerary with flights, hotel, day-wise weather, places and
budget, in both human-readable text and clean JSON.

## Problem Statement
Planning a trip means switching between many websites for flights, hotels,
attractions and weather. This project automates that using a LangChain
tool-calling agent that reasons step by step and builds an optimized itinerary.

## Features
- Flight search (cheapest or fastest) from `flights.json`
- Hotel recommendation filtered by city, stars and price from `hotels.json`
- Places discovery by city, type and rating from `places.json`
- Live day-wise weather from the free Open-Meteo API (no API key needed)
- Budget estimation (flights + hotel + daily local expenses)
- Reasoning ("Why we selected this") and downloadable JSON output
- Streamlit interface with interactive filters

## Tech Stack
Python, LangChain, Groq LLM (`openai/gpt-oss-120b`), Open-Meteo API, Streamlit

## Project Structure
```
travel-planning-agent/
├── data/              # flights.json, hotels.json, places.json
├── tools/             # flight, hotel, places, weather, budget tools
├── agent/             # LangChain agent and system prompt
├── app.py             # Streamlit UI
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
5. Run the app:
   ```
   streamlit run app.py
   ```

## Usage
Choose source, destination, dates (3 to 7 days), flight preference and minimum
hotel stars in the sidebar, then click **Plan my trip**. Weather forecast works
for dates within the next ~16 days.

## How It Works
1. The agent reads the user query.
2. It calls the tools: flights (onward and return), hotels, places, weather, budget.
3. It builds a day-wise itinerary using only the data returned by the tools.
4. It returns a structured answer plus a JSON block.

## Notes
- The datasets are sample data, so flight dates and place names are synthetic.
- Cities supported: Bangalore, Chennai, Delhi, Goa, Hyderabad, Jaipur, Kolkata, Mumbai.