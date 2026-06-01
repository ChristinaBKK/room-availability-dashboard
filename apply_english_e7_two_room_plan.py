#!/usr/bin/env python3
"""Apply the approved two-room plan for English E-7."""

from __future__ import annotations

import json
import os
import urllib.parse

import requests

from allocate_candidate_rooms_june_2026 import exact_booking_exists
from analyze_candidate_room_alternatives import SUPABASE_KEY, SUPABASE_URL, fetch_existing_rows, overlaps


BOOKINGS_URL = f"{SUPABASE_URL}/rest/v1/bookings"
ROW = {
    "course": "English E-7",
    "program": "CIE",
    "block": "E",
    "teacher": "Cordelia Jiao",
}
BOOKING_ROWS = [
    {"date": "2026/06/11", "start_time": "08:20", "end_time": "09:45", "room": "B4011"},
    {"date": "2026/06/12", "start_time": "08:20", "end_time": "09:00", "room": "B4011"},
    {"date": "2026/06/15", "start_time": "08:20", "end_time": "09:45", "room": "B4011"},
    {"date": "2026/06/16", "start_time": "11:30", "end_time": "12:10", "room": "B4011"},
    {"date": "2026/06/18", "start_time": "08:20", "end_time": "09:45", "room": "B4041"},
    {"date": "2026/06/29", "start_time": "08:20", "end_time": "09:45", "room": "B4041"},
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


def clear_existing_assignments(session: requests.Session) -> int:
    cleared = 0
    for row in BOOKING_ROWS:
        params = urllib.parse.urlencode(
            {
                "date": f"eq.{row['date']}",
                "start_time": f"eq.{row['start_time']}",
                "end_time": f"eq.{row['end_time']}",
                "title": f"eq.{ROW['course']}",
                "teacher": f"eq.{ROW['teacher']}",
            },
            safe=".:() /",
        )
        response = session.delete(f"{BOOKINGS_URL}?{params}", timeout=60)
        if response.status_code not in (200, 204):
            response.raise_for_status()
        if response.status_code == 200:
            payload = response.json()
            if isinstance(payload, list):
                cleared += len(payload)
    return cleared


def validate_no_conflicts(existing: list[dict[str, str]]) -> None:
    for row in BOOKING_ROWS:
        booking = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": row["room"],
            "title": ROW["course"],
            "teacher": ROW["teacher"],
        }
        conflicts = [item for item in existing if overlaps(booking, item)]
        if conflicts:
            raise RuntimeError(json.dumps({"booking": booking, "conflicts": conflicts[:5]}, indent=2))


def insert_rows(session: requests.Session, existing: list[dict[str, str]]) -> dict[str, int]:
    inserted = 0
    skipped = 0
    for row in BOOKING_ROWS:
        payload = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": row["room"],
            "title": ROW["course"],
            "teacher": ROW["teacher"],
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
    cleared = clear_existing_assignments(session)
    rooms = sorted({row["room"] for row in BOOKING_ROWS})
    dates = sorted({row["date"] for row in BOOKING_ROWS})
    existing = fetch_existing_rows(session, rooms, dates, "bookings")
    validate_no_conflicts(existing)
    result = insert_rows(session, existing)
    print(json.dumps({"course": ROW["course"], "teacher": ROW["teacher"], "cleared": cleared, **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())