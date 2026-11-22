"""SQLite storage for saved trip plans."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "trips.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection that returns rows like dictionaries."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the trips table and its index if they do not exist."""
    with closing(get_connection()) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trips (
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_city TEXT NOT NULL,
                destination_city TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                num_days INTEGER NOT NULL,
                flight_preference TEXT,
                total_budget REAL,
                trip_json TEXT NOT NULL,
                readable_text TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips (created_at DESC)"
        )


def save_trip(
    source_city: str,
    destination_city: str,
    start_date: str,
    end_date: str,
    num_days: int,
    flight_preference: str,
    trip: dict,
    readable_text: str,
) -> int:
    """Save one trip plan and return its id."""
    total_budget = (trip.get("budget") or {}).get("total")
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            """
            INSERT INTO trips (
                source_city, destination_city, start_date, end_date, num_days,
                flight_preference, total_budget, trip_json, readable_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_city, destination_city, start_date, end_date, num_days,
                flight_preference, total_budget, json.dumps(trip), readable_text,
            ),
        )
        return cursor.lastrowid


def list_trips(limit: int = 20) -> list:
    """Return the most recent trips (summary only)."""
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT trip_id, source_city, destination_city, start_date, end_date,
                   num_days, total_budget, created_at
            FROM trips ORDER BY created_at DESC, trip_id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_trip(trip_id: int) -> Optional[dict]:
    """Return one saved trip with its full JSON and text, or None."""
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT * FROM trips WHERE trip_id = ?", (trip_id,)
        ).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["trip"] = json.loads(data.pop("trip_json"))
    data["readable"] = data.pop("readable_text") or ""
    return data


def delete_trip(trip_id: int) -> bool:
    """Delete one trip. Returns True if a row was removed."""
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute("DELETE FROM trips WHERE trip_id = ?", (trip_id,))
        return cursor.rowcount > 0