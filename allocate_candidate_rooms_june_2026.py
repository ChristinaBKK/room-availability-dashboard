#!/usr/bin/env python3
"""Build and optionally apply a global booking plan for workbook candidate rooms."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import requests

from analyze_candidate_room_alternatives import (
    BLOCK_SLOTS,
    SUPABASE_URL,
    candidate_rooms,
    fetch_existing_rows,
    normalize_room,
    parse_workbook,
    time_to_minutes,
)


PLAN_JSON_PATH = Path("candidate_room_allocation_plan.json")
PLAN_MD_PATH = Path("candidate_room_allocation_section.md")
UNRESOLVED_CSV_PATH = Path("candidate_room_unresolved_after_plan.csv")


def get_supabase_key() -> str:
    return (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or "sb_publishable_yvdyY62yUu7HgPw7wjy9XQ_jmcje9te"
    )


def overlaps(a: dict[str, str], b: dict[str, str]) -> bool:
    return (
        a["room"] == b["room"]
        and a["date"] == b["date"]
        and time_to_minutes(a["start_time"]) < time_to_minutes(b["end_time"])
        and time_to_minutes(a["end_time"]) > time_to_minutes(b["start_time"])
    )


def course_key(row: dict[str, str]) -> str:
    return " | ".join([row["course"], row["program"], row["block"], row["teacher"]])


def course_slots(row: dict[str, str], room: str) -> list[dict[str, str]]:
    return [
        {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "room": room,
        }
        for date, start_time, end_time in BLOCK_SLOTS[row["block"]]
    ]


def format_blocker(blocker: dict[str, str]) -> str:
    return (
        f"{blocker['room']} blocked by {blocker['source']} {blocker['conflict_time']} "
        f"{blocker['label']} ({blocker['teacher']}) on {blocker['date']}"
    )


def analyze_candidates() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    workbook_rows = [row for row in parse_workbook() if row["status"] == "Not Feasible"]
    all_candidate_rooms = sorted({room for row in workbook_rows for room in candidate_rooms(row["possible_rooms_raw"])})
    all_dates = sorted({date for slots in BLOCK_SLOTS.values() for date, _, _ in slots})

    session = requests.Session()
    key = get_supabase_key()
    session.headers.update({"apikey": key, "Authorization": f"Bearer {key}"})

    existing: list[dict[str, str]] = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, all_candidate_rooms, all_dates, table))

    analyses: list[dict[str, object]] = []
    for row in workbook_rows:
        candidates = []
        for index, room in enumerate(candidate_rooms(row["possible_rooms_raw"])):
            blockers = []
            for slot in course_slots(row, room):
                conflict = next((item for item in existing if overlaps(slot, item)), None)
                if conflict:
                    blockers.append(
                        {
                            "room": room,
                            "date": slot["date"],
                            "time": f"{slot['start_time']}-{slot['end_time']}",
                            "source": conflict["source"],
                            "conflict_time": f"{conflict['start_time']}-{conflict['end_time']}",
                            "label": conflict["label"],
                            "teacher": conflict["teacher"],
                        }
                    )
            candidates.append(
                {
                    "room": room,
                    "rank": index,
                    "feasible_live": not blockers,
                    "blockers": blockers,
                }
            )
        analyses.append(
            {
                "row": row,
                "key": course_key(row),
                "feasible_candidates": [candidate for candidate in candidates if candidate["feasible_live"]],
                "blocked_candidates": [candidate for candidate in candidates if not candidate["feasible_live"]],
            }
        )

    return analyses, existing


def planned_conflict(course: dict[str, object], room: str, assigned_slots: list[dict[str, str]]) -> bool:
    for slot in course_slots(course["row"], room):
        if any(overlaps(slot, other) for other in assigned_slots):
            return True
    return False


def choose_plan(analyses: list[dict[str, object]]) -> tuple[dict[str, str], list[dict[str, object]]]:
    allocatable = [item for item in analyses if item["feasible_candidates"]]
    allocatable.sort(key=lambda item: (len(item["feasible_candidates"]), item["key"]))

    best_assignment: dict[str, str] = {}
    best_score = (-1, float("inf"))

    def search(index: int, assignment: dict[str, str], assigned_slots: list[dict[str, str]], rank_sum: int) -> None:
        nonlocal best_assignment, best_score
        remaining = len(allocatable) - index
        if len(assignment) + remaining < best_score[0]:
            return
        if index >= len(allocatable):
            score = (len(assignment), -rank_sum)
            if score > best_score:
                best_score = score
                best_assignment = dict(assignment)
            return

        item = allocatable[index]
        for candidate in item["feasible_candidates"]:
            room = candidate["room"]
            if planned_conflict(item, room, assigned_slots):
                continue
            new_slots = assigned_slots + course_slots(item["row"], room)
            assignment[item["key"]] = room
            search(index + 1, assignment, new_slots, rank_sum + candidate["rank"])
            assignment.pop(item["key"], None)

        search(index + 1, assignment, assigned_slots, rank_sum)

    search(0, {}, [], 0)

    unresolved = []
    for item in analyses:
        if item["key"] in best_assignment:
            continue
        unresolved.append(item)
    return best_assignment, unresolved


def booking_rows_from_plan(analyses: list[dict[str, object]], assignment: dict[str, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    by_key = {item["key"]: item for item in analyses}
    for key, room in assignment.items():
        item = by_key[key]
        row = item["row"]
        for slot in course_slots(row, room):
            rows.append(
                {
                    "date": slot["date"],
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"],
                    "room": room,
                    "title": row["course"],
                    "teacher": row["teacher"],
                    "program": row["program"],
                    "block": row["block"],
                }
            )
    rows.sort(key=lambda row: (row["date"], row["start_time"], row["room"], row["title"], row["teacher"]))
    return rows


def write_unresolved_csv(unresolved: list[dict[str, object]], assignment: dict[str, str]) -> None:
    with UNRESOLVED_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "course",
                "program",
                "block",
                "teacher",
                "original_room",
                "workbook_candidates",
                "live_feasible_candidates",
                "status_after_plan",
                "notes",
            ]
        )
        for item in unresolved:
            row = item["row"]
            workbook_candidates = [candidate["room"] for candidate in item["feasible_candidates"] + item["blocked_candidates"]]
            live_feasible = [candidate["room"] for candidate in item["feasible_candidates"]]
            if live_feasible:
                notes = "Live-feasible candidates exist, but all of them are consumed by higher-priority planned allocations."
            elif item["blocked_candidates"]:
                notes = "; ".join(format_blocker(candidate["blockers"][0]) for candidate in item["blocked_candidates"][:2] if candidate["blockers"])
            else:
                notes = "Workbook entry was blank or marked ignore."
            writer.writerow(
                [
                    row["course"],
                    row["program"],
                    row["block"],
                    row["teacher"],
                    row["room"],
                    ", ".join(workbook_candidates) or "No candidate provided",
                    ", ".join(live_feasible) or "None",
                    "Unresolved",
                    notes,
                ]
            )


def find_existing_booking(session: requests.Session, row: dict[str, str]) -> bool:
    params = (
        f"select=id&date=eq.{row['date']}&start_time=eq.{row['start_time']}&end_time=eq.{row['end_time']}"
        f"&room=eq.{requests.utils.quote(row['room'], safe='')}&title=eq.{requests.utils.quote(row['title'], safe='')}"
        f"&teacher=eq.{requests.utils.quote(row['teacher'], safe='')}&limit=1"
    )
    response = session.get(f"{SUPABASE_URL}/rest/v1/bookings?{params}", timeout=60)
    response.raise_for_status()
    return bool(response.json())


def exact_booking_exists(row: dict[str, str], existing_rows: list[dict[str, str]]) -> bool:
    return any(
        existing["date"] == row["date"]
        and existing["start_time"] == row["start_time"]
        and existing["end_time"] == row["end_time"]
        and existing["room"] == normalize_room(row["room"])
        and existing["label"] == row["title"]
        and existing["teacher"] == row["teacher"]
        for existing in existing_rows
    )


def insert_plan(session: requests.Session, rows: list[dict[str, str]]) -> dict[str, object]:
    rooms = sorted({normalize_room(row["room"]) for row in rows})
    dates = sorted({row["date"] for row in rows})
    existing_rows = fetch_existing_rows(session, rooms, dates, "bookings")
    inserted = []
    skipped = []
    failed = []
    for row in rows:
        payload = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": normalize_room(row["room"]),
            "title": row["title"],
            "teacher": row["teacher"],
        }
        if exact_booking_exists(payload, existing_rows):
            skipped.append(row)
            continue
        response = session.post(f"{SUPABASE_URL}/rest/v1/bookings", json=payload, timeout=60)
        if response.status_code in (200, 201):
            inserted.append(row)
            existing_rows.append(
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
            continue
        failed.append({"row": row, "status_code": response.status_code, "response": response.text[:500]})
    return {"inserted": inserted, "skipped": skipped, "failed": failed}


def verify_plan(session: requests.Session, rows: list[dict[str, str]]) -> tuple[int, int]:
    rooms = sorted({normalize_room(row["room"]) for row in rows})
    dates = sorted({row["date"] for row in rows})
    existing_rows = fetch_existing_rows(session, rooms, dates, "bookings")
    verified = 0
    missing = 0
    for row in rows:
        if exact_booking_exists(row, existing_rows):
            verified += 1
        else:
            missing += 1
    return verified, missing


def build_markdown(
    analyses: list[dict[str, object]],
    assignment: dict[str, str],
    unresolved: list[dict[str, object]],
    booking_rows: list[dict[str, str]],
    execution: dict[str, object] | None,
) -> str:
    assigned_lookup = {item["key"]: item for item in analyses if item["key"] in assignment}
    lines = [
        "## Candidate Room Allocation Plan",
        "",
        "This section converts the per-course workbook feasibility check into one conflict-free allocation plan across the remaining blocked courses. Each planned course keeps one room consistently across all of its block slots.",
        "",
        "### Allocation Summary",
        "",
        f"- Courses reviewed from workbook: {len(analyses)}",
        f"- Courses with at least one live-feasible candidate: {sum(1 for item in analyses if item['feasible_candidates'])}",
        f"- Courses allocated in one global plan: {len(assignment)}",
        f"- Booking rows represented by the plan: {len(booking_rows)}",
        f"- Courses still unresolved after global allocation: {len(unresolved)}",
        f"- Unresolved export: {UNRESOLVED_CSV_PATH.name}",
        "",
        "### Planned Allocations",
        "",
        "| Course | Program | Block | Teacher | Chosen room | Other live-feasible options | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for key in sorted(assignment):
        item = assigned_lookup[key]
        chosen = assignment[key]
        alternatives = [candidate["room"] for candidate in item["feasible_candidates"] if candidate["room"] != chosen]
        note = "First live-feasible workbook option kept." if item["feasible_candidates"] and item["feasible_candidates"][0]["room"] == chosen else "Chosen to keep the global plan conflict-free."
        row = item["row"]
        lines.append(
            f"| {row['course']} | {row['program']} | {row['block']} | {row['teacher']} | {chosen} | {', '.join(alternatives) or 'None'} | {note} |"
        )

    lines.extend(
        [
            "",
            "### Still Unresolved After Global Allocation",
            "",
            "| Course | Program | Block | Teacher | Workbook candidates | Why unresolved |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for item in unresolved:
        row = item["row"]
        workbook_candidates = [candidate["room"] for candidate in item["feasible_candidates"] + item["blocked_candidates"]]
        if item["feasible_candidates"]:
            reason = "Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan."
        elif item["blocked_candidates"]:
            first = item["blocked_candidates"][0]["blockers"][0] if item["blocked_candidates"][0]["blockers"] else None
            reason = format_blocker(first) if first else "No live-feasible candidate from workbook."
        else:
            reason = "Workbook entry was blank or marked ignore."
        lines.append(
            f"| {row['course']} | {row['program']} | {row['block']} | {row['teacher']} | {', '.join(workbook_candidates) or 'No candidate provided'} | {reason} |"
        )

    if execution is None:
        lines.extend([
            "",
            "### Execution Status",
            "",
            "Plan generated only. Bookings have not been inserted yet.",
            "",
        ])
    else:
        lines.extend(
            [
                "",
                "### Execution Status",
                "",
                f"- Planned booking rows: {len(booking_rows)}",
                f"- Inserted booking rows this run: {execution['inserted_booking_rows']}",
                f"- Skipped existing booking rows: {execution['skipped_existing_booking_rows']}",
                f"- Failed booking rows: {execution['failed_booking_rows']}",
                f"- Verified booking rows present after run: {execution['verified_booking_rows']}",
                f"- Missing after verification: {execution['missing_after_verification']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_outputs(
    analyses: list[dict[str, object]],
    assignment: dict[str, str],
    unresolved: list[dict[str, object]],
    booking_rows: list[dict[str, str]],
    execution: dict[str, object] | None,
) -> None:
    PLAN_JSON_PATH.write_text(
        json.dumps(
            {
                "summary": {
                    "courses_reviewed": len(analyses),
                    "courses_with_live_feasible_candidates": sum(1 for item in analyses if item["feasible_candidates"]),
                    "courses_allocated": len(assignment),
                    "booking_rows": len(booking_rows),
                    "unresolved_courses": len(unresolved),
                },
                "allocations": [
                    {
                        "course": item["row"]["course"],
                        "program": item["row"]["program"],
                        "block": item["row"]["block"],
                        "teacher": item["row"]["teacher"],
                        "room": assignment[item["key"]],
                    }
                    for item in analyses
                    if item["key"] in assignment
                ],
                "booking_rows": booking_rows,
                "execution": execution,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    PLAN_MD_PATH.write_text(build_markdown(analyses, assignment, unresolved, booking_rows, execution), encoding="utf-8")
    write_unresolved_csv(unresolved, assignment)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Insert the planned booking rows into the bookings table")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    analyses, _existing = analyze_candidates()
    assignment, unresolved = choose_plan(analyses)
    booking_rows = booking_rows_from_plan(analyses, assignment)

    key = get_supabase_key()
    session = requests.Session()
    session.headers.update({"apikey": key, "Authorization": f"Bearer {key}"})

    execution = None
    if args.apply:
        insert_result = insert_plan(session, booking_rows)
        verified, missing = verify_plan(session, booking_rows)
        execution = {
            "inserted_booking_rows": len(insert_result["inserted"]),
            "skipped_existing_booking_rows": len(insert_result["skipped"]),
            "failed_booking_rows": len(insert_result["failed"]),
            "verified_booking_rows": verified,
            "missing_after_verification": missing,
            "failed": insert_result["failed"],
        }

    write_outputs(analyses, assignment, unresolved, booking_rows, execution)

    print(PLAN_JSON_PATH)
    print(PLAN_MD_PATH)
    print(UNRESOLVED_CSV_PATH)
    print(
        json.dumps(
            {
                "courses_allocated": len(assignment),
                "booking_rows": len(booking_rows),
                "unresolved_courses": len(unresolved),
                "applied": bool(args.apply),
                **(execution or {}),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())