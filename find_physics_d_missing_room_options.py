#!/usr/bin/env python3
"""Find live-feasible room options for the remaining missing Physics D slots."""

from __future__ import annotations

import json
import os

import requests

from analyze_candidate_room_alternatives import SUPABASE_KEY, fetch_existing_rows, overlaps
from explore_unresolved_five_two_room_max import ALLOWED_ROOMS, SUPABASE_URL


SLOTS = [
    ("2026/06/11", "10:00", "11:25"),
    ("2026/06/12", "11:30", "12:10"),
    ("2026/06/15", "11:30", "12:10"),
    ("2026/06/16", "14:35", "16:00"),
    ("2026/06/17", "10:00", "11:25"),
    ("2026/06/18", "10:00", "11:25"),
    ("2026/06/29", "11:30", "12:10"),
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
    session.headers.update({"apikey": key, "Authorization": f"Bearer {key}"})
    return session


def main() -> int:
    session = get_session()
    rooms = sorted(ALLOWED_ROOMS)
    dates = sorted({date for date, _, _ in SLOTS})
    existing = []
    for table in ("bookings", "schedule", "room_sessions"):
        existing.extend(fetch_existing_rows(session, rooms, dates, table))

    available_all = []
    per_slot = {}
    for room in rooms:
        is_available_all = True
        for date, start_time, end_time in SLOTS:
            booking = {
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "room": room,
                "title": "Physics D",
                "teacher": "Faisal Qureshi",
            }
            if any(overlaps(booking, row) for row in existing):
                is_available_all = False
                break
        if is_available_all:
            available_all.append(room)

    for date, start_time, end_time in SLOTS:
        slot_rooms = []
        for room in rooms:
            booking = {
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "room": room,
                "title": "Physics D",
                "teacher": "Faisal Qureshi",
            }
            if not any(overlaps(booking, row) for row in existing):
                slot_rooms.append(room)
        per_slot[f"{date} {start_time}-{end_time}"] = slot_rooms

    print(json.dumps({"available_all_slots": available_all, "per_slot": per_slot}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())