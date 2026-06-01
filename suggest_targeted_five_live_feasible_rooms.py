#!/usr/bin/env python3
"""Suggest live-feasible rooms for the current five-row follow-up set."""

from __future__ import annotations

import csv
import json
import os
import re
import urllib.parse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import requests

from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, SUPABASE_URL, fetch_existing_rows, normalize_room, overlaps
from apply_remaining_15_user_decisions import USER_DECISIONS
from export_unresolved_csv_to_xlsx import build_sheet_xml


SOURCE_RESULTS = Path("remaining_15_user_decisions_results.csv")
OUT_CSV = Path("targeted_five_live_feasible_rooms.csv")
OUT_XLSX = Path("targeted_five_live_feasible_rooms.xlsx")
OUT_JSON = Path("targeted_five_live_feasible_rooms.json")
OUT_MD = Path("targeted_five_live_feasible_rooms.md")

TARGET_KEYS = [
    ("Economics B-1", "CIE", "B", "Helgaard Le Roux"),
    ("Chinese D-1", "CIE", "D", "Miya Yang"),
    ("English E-2", "CIE", "E", "Jenna Wade Dunn"),
    ("English E-6", "CIE", "E", "Sherry Yuan"),
    ("English E-7", "CIE", "E", "Cordelia Jiao"),
]

EXTRA_EXCLUDED = {
    ("Economics B-1", "CIE", "B", "Helgaard Le Roux"): {"B1037"},
    ("English E-2", "CIE", "E", "Jenna Wade Dunn"): {"B1029"},
}

REGULAR_MATHS_D_KEY = ("Regular Maths D", "CIE", "D", "Joy Farhat")
REGULAR_MATHS_D_TEST_ROOM = "B3042"


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


def canonical_room(raw: str) -> str:
    text = normalize_room(raw)
    match = re.search(r"B\d{4}|B-SEMINAR ROOM A", text.upper())
    if not match:
        return ""
    token = match.group(0)
    return "B-Seminar Room A" if token == "B-SEMINAR ROOM A" else token


def room_sort_key(room: str) -> tuple[int, str]:
    if room == "B-Seminar Room A":
        return (999999, room)
    return (int(room[1:]), room)


def load_rows() -> list[dict[str, str]]:
    with SOURCE_RESULTS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["course"], row["program"], row["block"], row["teacher"])


def booking_rows_for(row: dict[str, str], room: str) -> list[dict[str, str]]:
    return [
        {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "room": canonical_room(room),
            "title": row["course"],
            "teacher": row["teacher"],
            "program": row["program"],
            "block": row["block"],
        }
        for date, start_time, end_time in BLOCK_SLOTS[row["block"]]
    ]


def booking_signature(row: dict[str, str]) -> set[tuple[str, str, str, str, str]]:
    return {
        (slot["date"], slot["start_time"], slot["end_time"], slot["title"], slot["teacher"])
        for slot in booking_rows_for(row, row.get("assigned_room") or "B0000")
    }


def fetch_room_pool(session: requests.Session, dates: list[str]) -> list[str]:
    date_filter = urllib.parse.quote(
        ",".join(f"date.eq.{date}" for date in sorted(set(dates + [date.replace('/', '-') for date in dates]))),
        safe=",.=()",
    )
    rooms = set()
    for table in ("schedule", "bookings", "room_sessions"):
        response = session.get(
            f"{SUPABASE_URL}/rest/v1/{table}?select=room&or=({date_filter})&limit=5000",
            timeout=60,
        )
        response.raise_for_status()
        for item in response.json():
            room = canonical_room(item.get("room", ""))
            if room:
                rooms.add(room)
    rooms.add(REGULAR_MATHS_D_TEST_ROOM)
    return sorted(rooms, key=room_sort_key)


def decision_forbidden_rooms(key: tuple[str, str, str, str]) -> set[str]:
    decision = USER_DECISIONS.get(key, {})
    forbidden = {canonical_room(room) for room in decision.get("forbidden_rooms", [])}
    forbidden |= {canonical_room(room) for room in EXTRA_EXCLUDED.get(key, set())}
    return {room for room in forbidden if room}


def preferred_room(row: dict[str, str], forbidden: set[str]) -> str:
    requested_room = canonical_room(row.get("requested_room", ""))
    if requested_room and requested_room not in forbidden:
        return requested_room
    return ""


def is_live_feasible(row: dict[str, str], room: str, existing: list[dict[str, str]]) -> bool:
    return not any(overlaps(slot, conflict) for slot in booking_rows_for(row, room) for conflict in existing)


def remove_target_bookings(existing: list[dict[str, str]], target_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    signatures = set()
    for row in target_rows:
        for date, start_time, end_time in BLOCK_SLOTS[row["block"]]:
            signatures.add((date, start_time, end_time, row["course"], row["teacher"]))
    filtered = []
    for conflict in existing:
        signature = (conflict["date"], conflict["start_time"], conflict["end_time"], conflict["label"], conflict["teacher"])
        if conflict["source"] == "bookings" and signature in signatures:
            continue
        filtered.append(conflict)
    return filtered


def build_candidates(rows: list[dict[str, str]], room_pool: list[str], existing: list[dict[str, str]]) -> list[dict[str, object]]:
    items = []
    for row in rows:
        key = row_key(row)
        forbidden = decision_forbidden_rooms(key)
        requested = preferred_room(row, forbidden)
        available = [room for room in room_pool if room not in forbidden and is_live_feasible(row, room, existing)]
        ordered = []
        if requested and requested in available:
            ordered.append({"room": requested, "rank": 0})
        ordered.extend(
            {"room": room, "rank": index + 1 if requested and room != requested else index}
            for index, room in enumerate(room for room in available if room != requested)
        )
        items.append(
            {
                "row": row,
                "key": key,
                "forbidden": sorted(forbidden, key=room_sort_key),
                "requested": requested,
                "available": available,
                "ordered": ordered,
            }
        )
    return items


def planned_conflict(row: dict[str, str], room: str, assigned_slots: list[dict[str, str]]) -> bool:
    return any(overlaps(slot, other) for slot in booking_rows_for(row, room) for other in assigned_slots)


def choose_best_plan(items: list[dict[str, object]]) -> dict[tuple[str, str, str, str], str]:
    ordered_items = sorted(items, key=lambda item: (len(item["ordered"]), item["key"]))
    best_assignment: dict[tuple[str, str, str, str], str] = {}
    best_score = (-1, float("inf"))

    def search(index: int, assignment: dict[tuple[str, str, str, str], str], assigned_slots: list[dict[str, str]], rank_sum: int) -> None:
        nonlocal best_assignment, best_score
        if index == len(ordered_items):
            score = (len(assignment), rank_sum)
            if score[0] > best_score[0] or (score[0] == best_score[0] and score[1] < best_score[1]):
                best_assignment = dict(assignment)
                best_score = score
            return
        remaining = len(ordered_items) - index
        if len(assignment) + remaining < best_score[0]:
            return

        item = ordered_items[index]
        for candidate in item["ordered"]:
            room = candidate["room"]
            if planned_conflict(item["row"], room, assigned_slots):
                continue
            assignment[item["key"]] = room
            search(index + 1, assignment, assigned_slots + booking_rows_for(item["row"], room), rank_sum + candidate["rank"])
            assignment.pop(item["key"], None)

        search(index + 1, assignment, assigned_slots, rank_sum)

    search(0, {}, [], 0)
    return best_assignment


def regular_maths_d_status(row: dict[str, str], existing: list[dict[str, str]]) -> dict[str, str]:
    feasible = is_live_feasible(row, REGULAR_MATHS_D_TEST_ROOM, existing)
    return {
        "course": row["course"],
        "test_room": REGULAR_MATHS_D_TEST_ROOM,
        "status": "Live-feasible" if feasible else "Not live-feasible",
    }


def write_csv(rows: list[dict[str, str]]) -> None:
    headers = list(rows[0].keys()) if rows else []
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(rows: list[dict[str, str]]) -> None:
    headers = list(rows[0].keys()) if rows else []
    table = [headers] + [[row.get(header, "") for header in headers] for row in rows]
    with ZipFile(OUT_XLSX, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
            '</Types>',
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            '</Relationships>',
        )
        zf.writestr(
            "docProps/core.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">'
            '<dc:title>Targeted Five Live Feasible Rooms</dc:title>'
            '<dc:creator>GitHub Copilot</dc:creator>'
            '</cp:coreProperties>',
        )
        zf.writestr(
            "docProps/app.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>GitHub Copilot</Application></Properties>',
        )
        zf.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Suggestions" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(table))


def write_markdown(rows: list[dict[str, str]], regular_maths_d: dict[str, str]) -> None:
    lines = [
        "# Targeted Five Live-Feasible Rooms",
        "",
        "This file lists the current live-feasible rooms for the five follow-up rows that still need alternatives, using the latest live state while ignoring those rows' own current bookings.",
        "",
        f"- Regular Maths D check: {regular_maths_d['test_room']} -> {regular_maths_d['status']}",
        "",
        "| Course | Requested room | Excluded rooms | Best global pick | Available room count | Top live-feasible rooms |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['course']} | {row['requested_room'] or 'None'} | {row['excluded_rooms'] or 'None'} | {row['best_global_pick'] or 'None'} | {row['available_room_count']} | {row['top_live_feasible_rooms']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    all_rows = load_rows()
    row_map = {row_key(row): row for row in all_rows}
    target_rows = [row_map[key] for key in TARGET_KEYS]
    regular_maths_d_row = row_map[REGULAR_MATHS_D_KEY]

    session = get_session()
    dates = sorted({date for slots in BLOCK_SLOTS.values() for date, _, _ in slots})
    room_pool = fetch_room_pool(session, dates)
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, room_pool, dates, table))
    existing = remove_target_bookings(existing, target_rows)

    items = build_candidates(target_rows, room_pool, existing)
    best_plan = choose_best_plan(items)
    regular_maths_d = regular_maths_d_status(regular_maths_d_row, existing)

    output_rows = []
    for item in items:
        row = item["row"]
        output_rows.append(
            {
                "course": row["course"],
                "program": row["program"],
                "block": row["block"],
                "teacher": row["teacher"],
                "requested_room": item["requested"],
                "excluded_rooms": ", ".join(item["forbidden"]),
                "best_global_pick": best_plan.get(item["key"], ""),
                "available_room_count": str(len(item["available"])),
                "top_live_feasible_rooms": ", ".join(item["available"][:12]) or "None found",
            }
        )

    write_csv(output_rows)
    write_xlsx(output_rows)
    write_markdown(output_rows, regular_maths_d)
    OUT_JSON.write_text(json.dumps({"rows": output_rows, "regular_maths_d": regular_maths_d}, indent=2), encoding="utf-8")

    print(OUT_CSV)
    print(OUT_XLSX)
    print(OUT_MD)
    print(OUT_JSON)
    print(json.dumps({"rows": len(output_rows), "regular_maths_d": regular_maths_d}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())