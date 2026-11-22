const CITIES = ["Bangalore", "Chennai", "Delhi", "Goa", "Hyderabad", "Jaipur", "Kolkata", "Mumbai"];
const $ = (id) => document.getElementById(id);
let currentTrip = null;

/* ---------- helpers ---------- */
function esc(value) {
  const div = document.createElement("div");
  div.textContent = String(value ?? "");
  return div.innerHTML;
}

function money(value) {
  return "₹" + Number(value || 0).toLocaleString("en-IN");
}

function localDate(offsetDays) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${month}-${day}`;
}

function weatherIcon(condition) {
  const c = String(condition || "").toLowerCase();
  if (c.includes("thunder")) return "⛈️";
  if (c.includes("rain") || c.includes("drizzle")) return "🌧️";
  if (c.includes("fog")) return "🌫️";
  if (c.includes("overcast")) return "☁️";
  if (c.includes("partly")) return "⛅";
  if (c.includes("mainly clear")) return "🌤️";
  if (c.includes("clear")) return "☀️";
  return "🌡️";
}

function downloadBlob(blob, fileName) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

/* ---------- setup ---------- */
function setupForm() {
  CITIES.forEach((city) => {
    $("source").add(new Option(city, city));
    $("destination").add(new Option(city, city));
  });
  $("source").value = "Hyderabad";
  $("destination").value = "Goa";
  $("start_date").value = localDate(3);
  $("end_date").value = localDate(5);
}

function setupTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      tab.classList.add("active");
      $(tab.dataset.tab).classList.add("active");
    });
  });
}

/* ---------- rendering ---------- */
function flightLeg(label, leg) {
  if (!leg || !leg.price) {
    return `<div class="leg"><strong>${label}</strong>No flight in the data</div>`;
  }
  return `<div class="leg"><strong>${label}: ${esc(leg.airline)}</strong>${esc(leg.flight_id)} · ${money(leg.price)}</div>`;
}

function renderCards(trip) {
  const flight = trip.flight || {};
  $("flight-card").innerHTML = flightLeg("Onward", flight.onward) + flightLeg("Return", flight.return);

  const hotel = trip.hotel || {};
  $("hotel-card").innerHTML = `
    <div class="leg"><strong>${esc(hotel.name)}</strong>${esc(hotel.stars)} ★</div>
    <div class="kv"><span>Per night</span><span>${money(hotel.price_per_night)}</span></div>
    <div class="kv"><span>Nights</span><span>${esc(hotel.nights)}</span></div>`;

  const budget = trip.budget || {};
  $("budget-card").innerHTML = `
    <div class="big-price">${money(budget.total)}</div>
    <div class="kv"><span>Flights</span><span>${money(budget.flight)}</span></div>
    <div class="kv"><span>Hotel</span><span>${money(budget.hotel)}</span></div>
    <div class="kv"><span>Food & local</span><span>${money(budget.food_and_local_travel)}</span></div>`;
}

function renderItinerary(trip) {
  const days = trip.itinerary || [];
  $("tab-itinerary").innerHTML = days.length
    ? days.map((day) => `
        <div class="day-card">
          <h4>Day ${esc(day.day)} · ${esc(day.date)}</h4>
          ${(day.places || []).map((p) => `<span class="chip">📍 ${esc(p)}</span>`).join("")}
        </div>`).join("")
    : "<p class='muted'>No itinerary available.</p>";
}

function renderWeather(trip) {
  const days = trip.weather || [];
  $("tab-weather").innerHTML = days.length
    ? `<div class="weather-grid">${days.map((d) => `
        <div class="weather-card">
          <div class="muted">${esc(d.date)}</div>
          <div class="w-icon">${weatherIcon(d.condition)}</div>
          <div class="w-temp">${esc(d.max_temp_c)}° / ${esc(d.min_temp_c)}°</div>
          <div>${esc(d.condition)}</div>
        </div>`).join("")}</div>`
    : "<p class='muted'>Weather not available.</p>";
}

function renderDetails(readable) {
  const panel = $("tab-details");
  if (window.marked) {
    panel.innerHTML = marked.parse(readable);
  } else {
    panel.innerHTML = `<pre>${esc(readable)}</pre>`;
  }
}

function renderSteps(steps) {
  $("tab-steps").innerHTML = (steps || []).map((step, index) => `
    <div class="step-item">
      <div class="step-title">Step ${index + 1}: ${esc(step.tool)}</div>
      <pre>${esc(JSON.stringify(step.input, null, 2))}</pre>
      <pre>${esc(String(step.output).slice(0, 500))}</pre>
    </div>`).join("") || "<p class='muted'>No steps recorded.</p>";
}

function renderResults(data, form) {
  const trip = data.trip;
  currentTrip = trip;

  $("trip-title").textContent = `Your trip: ${form.source} → ${form.destination}`;
  $("trip-dates").textContent = `${form.start_date} to ${form.end_date}`;

  if (trip) {
    renderCards(trip);
    renderItinerary(trip);
    renderWeather(trip);
    $("tab-json").innerHTML = `<pre>${esc(JSON.stringify(trip, null, 2))}</pre>`;
  } else {
    ["flight-card", "hotel-card", "budget-card"].forEach((id) => { $(id).innerHTML = ""; });
    $("tab-itinerary").innerHTML = "<p class='muted'>Structured data missing. See the Full plan tab.</p>";
    $("tab-weather").innerHTML = "";
    $("tab-json").innerHTML = "<p class='muted'>JSON not available for this plan.</p>";
  }
  renderDetails(data.readable || "");
  renderSteps(data.steps);

  $("results").classList.remove("hidden");
  $("results").scrollIntoView({ behavior: "smooth" });
}

/* ---------- submit ---------- */
async function planTrip(event) {
  event.preventDefault();
  const form = {
    source: $("source").value,
    destination: $("destination").value,
    start_date: $("start_date").value,
    end_date: $("end_date").value,
    flight_preference: $("flight_preference").value,
    min_stars: Number($("min_stars").value),
    extra_notes: $("extra_notes").value,
  };

  $("error").classList.add("hidden");
  $("results").classList.add("hidden");
  $("loading").classList.remove("hidden");
  $("plan-btn").disabled = true;

  try {
    const response = await fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Something went wrong");
    }
    renderResults(data, form);
  } catch (error) {
    $("error").textContent = error.message;
    $("error").classList.remove("hidden");
  } finally {
    $("loading").classList.add("hidden");
    $("plan-btn").disabled = false;
  }
}

/* ---------- downloads ---------- */
$("download-json").addEventListener("click", () => {
  if (!currentTrip) return;
  const blob = new Blob([JSON.stringify(currentTrip, null, 2)], { type: "application/json" });
  downloadBlob(blob, "trip.json");
});

$("download-pdf").addEventListener("click", async () => {
  if (!currentTrip) return;
  const response = await fetch("/api/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(currentTrip),
  });
  if (response.ok) downloadBlob(await response.blob(), "trip.pdf");
});

/* ---------- start ---------- */
setupForm();
setupTabs();
$("trip-form").addEventListener("submit", planTrip);