#!/usr/bin/env python3
"""Verify the candidate-room allocation plan recorded in the markdown report."""

from __future__ import annotations

import json
import os
from pathlib import Path
import csv

import requests

from allocate_candidate_rooms_june_2026 import exact_booking_exists
from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, fetch_existing_rows, normalize_room


REPORT_PATH = Path("course_room_feasibility_june_2026.md")
OUT_PATH = Path("candidate_room_plan_report_verification.json")
UNRESOLVED_CSV_PATH = Path("candidate_room_unresolved_after_plan.csv")


def parse_plan_rows() -> list[dict[str, str]]:
    text = REPORT_PATH.read_text(encoding="utf-8")
    start = text.index("### Planned Allocations\n")
    end = text.index("\n### Still Unresolved After Global Allocation\n", start)
    lines = [line.strip() for line in text[start:end].splitlines()]
    plan_rows = []
    for line in lines:
        if not line.startswith("|"):
            continue
        if "Chosen room" in line or line.startswith("| ---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 7:
            continue
        plan_rows.append(
            {
                "course": parts[0],
                "program": parts[1],
                "block": parts[2],
                "teacher": parts[3],
                "room": parts[4],
            }
        )
    return plan_rows


def parse_unresolved_rows() -> list[dict[str, str]]:
    text = REPORT_PATH.read_text(encoding="utf-8")
    start = text.index("### Still Unresolved After Global Allocation\n")
    end = text.index("\n### Execution Status\n", start)
    lines = [line.strip() for line in text[start:end].splitlines()]
    unresolved_rows = []
    for line in lines:
        if not line.startswith("|"):
            continue
        if "Why unresolved" in line or line.startswith("| ---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 6:
            continue
        unresolved_rows.append(
            {
                "course": parts[0],
                "program": parts[1],
                "block": parts[2],
                "teacher": parts[3],
                "workbook_candidates": parts[4],
                "reason": parts[5],
            }
        )
    return unresolved_rows


def write_unresolved_csv(rows: list[dict[str, str]]) -> None:
    with UNRESOLVED_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["course", "program", "block", "teacher", "workbook_candidates", "reason"],
        )
        writer.writeheader()
        writer.writerows(rows)


def booking_rows(plan_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for item in plan_rows:
        for date, start_time, end_time in BLOCK_SLOTS[item["block"]]:
            rows.append(
                {
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "room": normalize_room(item["room"]),
                    "title": item["course"],
                    "teacher": item["teacher"],
                    "program": item["program"],
                    "block": item["block"],
                }
            )
    return rows


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
    plan_rows = parse_plan_rows()
    unresolved_rows = parse_unresolved_rows()
    rows = booking_rows(plan_rows)
    session = get_session()
    existing = fetch_existing_rows(
        session,
        sorted({row["room"] for row in rows}),
        sorted({row["date"] for row in rows}),
        "bookings",
    )
    present = [row for row in rows if exact_booking_exists(row, existing)]
    missing = [row for row in rows if not exact_booking_exists(row, existing)]
    payload = {
        "planned_courses": len(plan_rows),
        "planned_booking_rows": len(rows),
        "verified_booking_rows": len(present),
        "missing_after_verification": len(missing),
        "unresolved_courses": len(unresolved_rows),
        "unresolved_csv": UNRESOLVED_CSV_PATH.name,
        "missing_rows": missing,
    }
    write_unresolved_csv(unresolved_rows)
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(OUT_PATH)
    print(UNRESOLVED_CSV_PATH)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())