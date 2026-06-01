#!/usr/bin/env python3
"""Rename Faisal's June physics booking titles to the official course names."""

from __future__ import annotations

import json
import os

import requests

from analyze_candidate_room_alternatives import SUPABASE_KEY, SUPABASE_URL


UPDATES = [
    ("G10 TT Physics Block A", "Physics A-1"),
    ("G10 TT Physics Block A ", "Physics A-1"),
    ("G10 TT Physics Block A Summit", "Physics A-2 (Summit)"),
    ("G10 TT Physics Block A Summit ", "Physics A-2 (Summit)"),
    ("G10 TT Physics Block A EU", "Physics A-3 (EU)"),
    ("G10 TT Physics Block A EU ", "Physics A-3 (EU)"),
    ("G10 TT Physics Block B-1", "Physics B-1"),
    ("G10 TT Physics Block B-2", "Physics B-2"),
    ("G10 TT Physics Block D", "Physics D"),
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
    session.headers.update(
        {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=representation",
        }
    )
    return session


def main() -> int:
    session = get_session()
    results = []
    for old_title, new_title in UPDATES:
        response = session.patch(
            f"{SUPABASE_URL}/rest/v1/bookings",
            params={
                "title": f"eq.{old_title}",
                "teacher": "eq.Faisal Qureshi",
                "date": "gte.2026-06-01",
                "select": "date,start_time,end_time,room,title,teacher",
            },
            json={"title": new_title},
            timeout=60,
        )
        response.raise_for_status()
        rows = response.json()
        results.append(
            {
                "old_title": old_title,
                "new_title": new_title,
                "updated_rows": len(rows),
                "rows": rows,
            }
        )
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())