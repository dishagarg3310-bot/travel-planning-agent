"""PDF export for the generated trip itinerary."""
from fpdf import FPDF

CHAR_FIXES = {
    "\u20b9": "Rs ",
    "\u2011": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2605": "*",
}


def _text(value) -> str:
    """Make text safe for the built-in PDF font (latin-1 only)."""
    text = str(value)
    for old, new in CHAR_FIXES.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


class TripPDF(FPDF):
    """Small helper class with simple writing methods."""

    def heading(self, title: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 8, _text(title), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 11)

    def write_line(self, text: str) -> None:
        self.multi_cell(0, 6, _text(text), new_x="LMARGIN", new_y="NEXT")


def _flight_text(label: str, leg) -> str:
    """Build one line of text for a flight leg."""
    if not leg or not leg.get("price"):
        return f"{label}: no flight available in the data"
    return (
        f"{label}: {leg.get('airline', '')} ({leg.get('flight_id', '')}) "
        f"- Rs {leg.get('price')}"
    )


def build_trip_pdf(trip: dict) -> bytes:
    """Create a PDF from the trip JSON and return it as bytes."""
    summary = trip.get("trip_summary", {})
    pdf = TripPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    title = f"Trip: {summary.get('source', '')} to {summary.get('destination', '')}"
    pdf.cell(0, 10, _text(title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.write_line(
        f"Dates: {summary.get('start_date', '')} to {summary.get('end_date', '')} "
        f"({summary.get('num_days', '')} days)"
    )

    flight = trip.get("flight", {})
    pdf.heading("Flights")
    pdf.write_line(_flight_text("Onward", flight.get("onward")))
    pdf.write_line(_flight_text("Return", flight.get("return")))

    hotel = trip.get("hotel", {})
    pdf.heading("Hotel")
    pdf.write_line(
        f"{hotel.get('name', '')} - {hotel.get('stars', '')} star - "
        f"Rs {hotel.get('price_per_night', '')} per night x {hotel.get('nights', '')} nights"
    )

    pdf.heading("Weather")
    for day in trip.get("weather", []):
        pdf.write_line(
            f"{day.get('date', '')}: {day.get('condition', '')}, "
            f"{day.get('min_temp_c', '')} to {day.get('max_temp_c', '')} C"
        )

    pdf.heading("Day-wise Itinerary")
    for day in trip.get("itinerary", []):
        places = ", ".join(day.get("places", []))
        pdf.write_line(f"Day {day.get('day', '')} ({day.get('date', '')}): {places}")

    budget = trip.get("budget", {})
    pdf.heading("Budget (INR)")
    pdf.write_line(f"Flights: Rs {budget.get('flight', 0)}")
    pdf.write_line(f"Hotel: Rs {budget.get('hotel', 0)}")
    pdf.write_line(f"Food and local travel: Rs {budget.get('food_and_local_travel', 0)}")
    pdf.set_font("Helvetica", "B", 11)
    pdf.write_line(f"Total: Rs {budget.get('total', 0)}")
    pdf.set_font("Helvetica", "", 11)

    pdf.heading("Why we selected this")
    for reason in trip.get("reasoning", []):
        pdf.write_line(f"- {reason}")

    return bytes(pdf.output())