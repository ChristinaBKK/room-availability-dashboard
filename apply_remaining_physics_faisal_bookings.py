#!/usr/bin/env python3
"""Apply the remaining approved Faisal physics bookings for June 2026."""

from __future__ import annotations

import json
import os

import requests

from allocate_candidate_rooms_june_2026 import exact_booking_exists
from analyze_candidate_room_alternatives import SUPABASE_KEY, SUPABASE_URL, fetch_existing_rows, overlaps


BOOKINGS_URL = f"{SUPABASE_URL}/rest/v1/bookings"
TEACHER = "Faisal Qureshi"
BOOKING_ROWS = [
    {"title": "Physics B-1", "date": "2026/06/11", "start_time": "14:35", "end_time": "16:00", "room": "B3005"},
    {"title": "Physics B-1", "date": "2026/06/15", "start_time": "14:35", "end_time": "16:00", "room": "B3005"},
    {"title": "Physics B-1", "date": "2026/06/18", "start_time": "14:35", "end_time": "16:00", "room": "B3005"},
    {"title": "Physics B-1", "date": "2026/06/29", "start_time": "14:35", "end_time": "16:00", "room": "B3005"},
    {"title": "Physics B-2", "date": "2026/06/11", "start_time": "14:35", "end_time": "16:00", "room": "B3004"},
    {"title": "Physics B-2", "date": "2026/06/15", "start_time": "14:35", "end_time": "16:00", "room": "B3004"},
    {"title": "Physics B-2", "date": "2026/06/18", "start_time": "14:35", "end_time": "16:00", "room": "B3004"},
    {"title": "Physics B-2", "date": "2026/06/29", "start_time": "14:35", "end_time": "16:00", "room": "B3004"},
    {"title": "Physics D", "date": "2026/06/11", "start_time": "10:00", "end_time": "11:25", "room": "B4038"},
    {"title": "Physics D", "date": "2026/06/12", "start_time": "11:30", "end_time": "12:10", "room": "B4038"},
    {"title": "Physics D", "date": "2026/06/15", "start_time": "11:30", "end_time": "12:10", "room": "B4038"},
    {"title": "Physics D", "date": "2026/06/16", "start_time": "14:35", "end_time": "16:00", "room": "B4038"},
    {"title": "Physics D", "date": "2026/06/17", "start_time": "10:00", "end_time": "11:25", "room": "B4038"},
    {"title": "Physics D", "date": "2026/06/18", "start_time": "10:00", "end_time": "11:25", "room": "B4038"},
    {"title": "Physics D", "date": "2026/06/29", "start_time": "11:30", "end_time": "12:10", "room": "B4038"},
]


def get_session() -> requests.Session:
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or SUPABASE_KEY
    )
    session = requests.Session()
    session.headers.update({"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    return session


def validate_no_conflicts(existing: list[dict[str, str]]) -> None:
    for row in BOOKING_ROWS:
        booking = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": row["room"],
            "title": row["title"],
            "teacher": TEACHER,
        }
        if exact_booking_exists(booking, existing):
            continue
        conflicts = [item for item in existing if overlaps(booking, item)]
        if conflicts:
            raise RuntimeError(json.dumps({"booking": booking, "conflicts": conflicts[:10]}, indent=2))


def insert_rows(session: requests.Session, existing: list[dict[str, str]]) -> dict[str, int]:
    inserted = 0
    skipped = 0
    for row in BOOKING_ROWS:
        payload = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": row["room"],
            "title": row["title"],
            "teacher": TEACHER,
        }
        if exact_booking_exists(payload, existing):
            skipped += 1
            continue
        response = session.post(BOOKINGS_URL, json=payload, timeout=60)
        if response.status_code not in (200, 201):
            raise RuntimeError(response.text[:500])
        inserted += 1
        existing.append(
            {
                "source": "bookings",
                "date": payload["date"],
                "start_time": payload["start_time"],
                "end_time": payload["end_time"],
                "room": payload["room"],
                "label": payload["title"],
                "teacher": payload["teacher"],
            }
        )
    return {"inserted": inserted, "skipped": skipped}


def main() -> int:
    session = get_session()
    rooms = sorted({row["room"] for row in BOOKING_ROWS})
    dates = sorted({row["date"] for row in BOOKING_ROWS})
    existing = []
    for table in ("bookings", "schedule", "room_sessions"):
        existing.extend(fetch_existing_rows(session, rooms, dates, table))
    validate_no_conflicts(existing)
    result = insert_rows(session, existing)
    print(json.dumps({"teacher": TEACHER, **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())