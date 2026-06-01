#!/usr/bin/env python3
"""Remove the stray duplicate Physics D row left by an earlier failed insert attempt."""

from __future__ import annotations

import json
import os
import urllib.parse

import requests

from analyze_candidate_room_alternatives import SUPABASE_KEY, SUPABASE_URL


BOOKINGS_URL = f"{SUPABASE_URL}/rest/v1/bookings"


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
    params = urllib.parse.urlencode(
        {
            "date": "eq.2026/06/11",
            "start_time": "eq.10:00",
            "end_time": "eq.11:25",
            "room": "eq.B3011",
            "title": "eq.Physics D",
            "teacher": "eq.Faisal Qureshi",
            "select": "date,start_time,end_time,room,title,teacher",
        },
        safe=".:()/ ",
    )
    response = session.delete(f"{BOOKINGS_URL}?{params}", timeout=60)
    if response.status_code not in (200, 204):
        response.raise_for_status()
    payload = response.json() if response.status_code == 200 else []
    print(json.dumps({"deleted_rows": len(payload), "rows": payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())