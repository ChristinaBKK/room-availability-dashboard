#!/usr/bin/env python3
"""Apply the approved two-room plans for Chinese D-1 and English E-6."""

from __future__ import annotations

import json
import os
import urllib.parse

import requests

from allocate_candidate_rooms_june_2026 import exact_booking_exists
from analyze_candidate_room_alternatives import SUPABASE_KEY, SUPABASE_URL, fetch_existing_rows, overlaps


BOOKINGS_URL = f"{SUPABASE_URL}/rest/v1/bookings"
PLANS = [
    {
        "course": "Chinese D-1",
        "teacher": "Miya Yang",
        "rows": [
            {"date": "2026/06/10", "start_time": "10:00", "end_time": "11:25", "room": "B3010"},
            {"date": "2026/06/11", "start_time": "10:00", "end_time": "11:25", "room": "B3009"},
            {"date": "2026/06/12", "start_time": "11:30", "end_time": "12:10", "room": "B3009"},
            {"date": "2026/06/15", "start_time": "11:30", "end_time": "12:10", "room": "B3009"},
            {"date": "2026/06/16", "start_time": "14:35", "end_time": "16:00", "room": "B3009"},
            {"date": "2026/06/17", "start_time": "10:00", "end_time": "11:25", "room": "B3009"},
            {"date": "2026/06/18", "start_time": "10:00", "end_time": "11:25", "room": "B3009"},
            {"date": "2026/06/29", "start_time": "11:30", "end_time": "12:10", "room": "B3009"},
        ],
    },
    {
        "course": "English E-6",
        "teacher": "Sherry Yuan",
        "rows": [
            {"date": "2026/06/11", "start_time": "08:20", "end_time": "09:45", "room": "B3010"},
            {"date": "2026/06/12", "start_time": "08:20", "end_time": "09:00", "room": "B3010"},
            {"date": "2026/06/15", "start_time": "08:20", "end_time": "09:45", "room": "B3012"},
            {"date": "2026/06/16", "start_time": "11:30", "end_time": "12:10", "room": "B3012"},
            {"date": "2026/06/18", "start_time": "08:20", "end_time": "09:45", "room": "B3012"},
            {"date": "2026/06/29", "start_time": "08:20", "end_time": "09:45", "room": "B3012"},
        ],
    },
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


def clear_existing_assignments(session: requests.Session, course: str, teacher: str, rows: list[dict[str, str]]) -> int:
    cleared = 0
    for row in rows:
        params = urllib.parse.urlencode(
            {
                "date": f"eq.{row['date']}",
                "start_time": f"eq.{row['start_time']}",
                "end_time": f"eq.{row['end_time']}",
                "title": f"eq.{course}",
                "teacher": f"eq.{teacher}",
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


def validate_no_conflicts(course: str, teacher: str, rows: list[dict[str, str]], existing: list[dict[str, str]]) -> None:
    for row in rows:
        booking = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": row["room"],
            "title": course,
            "teacher": teacher,
        }
        conflicts = [item for item in existing if overlaps(booking, item)]
        if conflicts:
            raise RuntimeError(json.dumps({"booking": booking, "conflicts": conflicts[:5]}, indent=2))


def insert_rows(session: requests.Session, course: str, teacher: str, rows: list[dict[str, str]], existing: list[dict[str, str]]) -> dict[str, int]:
    inserted = 0
    skipped = 0
    for row in rows:
        payload = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": row["room"],
            "title": course,
            "teacher": teacher,
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
    results = []
    for plan in PLANS:
        course = plan["course"]
        teacher = plan["teacher"]
        rows = plan["rows"]
        cleared = clear_existing_assignments(session, course, teacher, rows)
        rooms = sorted({row["room"] for row in rows})
        dates = sorted({row["date"] for row in rows})
        existing = fetch_existing_rows(session, rooms, dates, "bookings")
        validate_no_conflicts(course, teacher, rows, existing)
        result = insert_rows(session, course, teacher, rows, existing)
        results.append({"course": course, "teacher": teacher, "cleared": cleared, **result})
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())