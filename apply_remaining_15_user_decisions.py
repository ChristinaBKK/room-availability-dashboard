#!/usr/bin/env python3
"""Apply the user's room decisions for the remaining 15 June rows."""

from __future__ import annotations

import csv
import json
import os
import re
import urllib.parse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import requests

from allocate_candidate_rooms_june_2026 import exact_booking_exists
from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, SUPABASE_URL, fetch_existing_rows, normalize_room, overlaps
from export_unresolved_csv_to_xlsx import build_sheet_xml


SOURCE_CSV = Path("candidate_room_remaining_blocked_results.csv")
OUT_CSV = Path("remaining_15_user_decisions_results.csv")
OUT_XLSX = Path("remaining_15_user_decisions_results.xlsx")
OUT_JSON = Path("remaining_15_user_decisions_results.json")
OUT_MD = Path("remaining_15_user_decisions_results.md")
UNRESOLVED_CSV = Path("remaining_15_user_decisions_unresolved.csv")
UNRESOLVED_XLSX = Path("remaining_15_user_decisions_unresolved.xlsx")
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
REPORT_HEADER = "## Remaining 15 User Room Decisions"
BOOKINGS_URL = f"{SUPABASE_URL}/rest/v1/bookings"
NONEXISTENT_ROOMS = {"B2038"}
LIMITED_ALTERNATIVES = [
    "B1034",
    "B2039",
    "B2040",
    "B2041",
    "B2042",
    "B2043",
    "B2044",
    "B3009",
    "B3010",
    "B3011",
    "B3012",
    "B3039",
    "B3040",
    "B3041",
    "B3042",
    "B3043",
    "B4009",
    "B4010",
    "B4011",
    "B4038",
    "B4039",
    "B4040",
    "B4041",
    "B4042",
    "B4043",
]


USER_DECISIONS = {
    ("Physics HL/SL", "IBDP", "B1", "Logan Tian"): {"mode": "use", "room": "B4012"},
    ("Economics B-1", "CIE", "B", "Helgaard Le Roux"): {"mode": "use", "room": "B4011"},
    ("Economics B-2 (Summit)", "CIE", "B", "Fahran Nzamy"): {"mode": "use", "room": "B2044", "allowed_rooms": LIMITED_ALTERNATIVES, "forbidden_rooms": ["B2014", "B1037", "B2022", "B2036"]},
    ("Art (Dual Dose)", "CIE", "B", "Mark Ford"): {"mode": "use", "room": "B3028"},
    ("Chemistry HL/SL", "IBDP", "C", "Judy Zhu"): {"mode": "use", "room": "B3004"},
    ("Regular Maths D", "CIE", "D", "Joy Farhat"): {"mode": "find_else", "allowed_rooms": LIMITED_ALTERNATIVES, "forbidden_rooms": ["B1037", "B2003", "B1011", "B1029"]},
    ("Fast Maths (Edexcel)", "CIE", "D", "Rajesh"): {"mode": "use", "room": "B1034"},
    ("Chemistry D", "CIE", "D", "Selina Sun"): {"mode": "use", "room": "B3005"},
    ("Chinese D-1", "CIE", "D", "Miya Yang"): {"mode": "find_else", "allowed_rooms": LIMITED_ALTERNATIVES, "forbidden_rooms": ["B1011", "B1029", "B1037", "B2003"]},
    ("Chinese D-2", "CIE", "D", "Ivy Zhu"): {"mode": "find_else", "allowed_rooms": LIMITED_ALTERNATIVES, "forbidden_rooms": ["B1029", "B1011", "B2003", "B1037"]},
    ("Business H/SL", "IBDP", "E", "Jennifer Jacobs-Kraft"): {"mode": "use", "room": "B3043", "allowed_rooms": ["B3043"], "forbidden_rooms": ["B1029"]},
    ("English E-2", "CIE", "E", "Jenna Wade Dunn"): {"mode": "use", "room": "B3043", "forbidden_rooms": ["B1011"]},
    ("English E-3", "CIE", "E", "Lim Wan"): {"mode": "use", "room": "B1034", "allowed_rooms": LIMITED_ALTERNATIVES, "forbidden_rooms": ["B1029", "B1011", "B1037", "B2003"]},
    ("English E-6", "CIE", "E", "Sherry Yuan"): {"mode": "find_else", "allowed_rooms": LIMITED_ALTERNATIVES, "forbidden_rooms": ["B2003", "B2004", "B2005", "B1011"]},
    ("English E-7", "CIE", "E", "Cordelia Jiao"): {"mode": "use", "room": "B1029", "allowed_rooms": LIMITED_ALTERNATIVES, "forbidden_rooms": ["B1037", "B1029", "B1011", "B2004"]},
}


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


def load_rows() -> list[dict[str, str]]:
    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["course"], row["program"], row["block"], row["teacher"])


def slot_rows_for(row: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "title": row["course"],
            "teacher": row["teacher"],
        }
        for date, start_time, end_time in BLOCK_SLOTS[row["block"]]
    ]


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


def decision_forbidden_rooms(decision: dict[str, object]) -> set[str]:
    return {
        room
        for room in (canonical_room(value) for value in decision.get("forbidden_rooms", []))
        if room and room not in NONEXISTENT_ROOMS
    }


def decision_allowed_rooms(decision: dict[str, object]) -> set[str]:
    return {
        room
        for room in (canonical_room(value) for value in decision.get("allowed_rooms", []))
        if room and room not in NONEXISTENT_ROOMS
    }


def decision_explicit_rooms() -> list[str]:
    rooms = set()
    for decision in USER_DECISIONS.values():
        room = canonical_room(decision.get("room", ""))
        if room and room not in NONEXISTENT_ROOMS:
            rooms.add(room)
        rooms.update(decision_allowed_rooms(decision))
    return sorted(rooms, key=room_sort_key)


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
    return sorted(rooms)


def room_sort_key(room: str) -> tuple[int, str]:
    if room == "B-Seminar Room A":
        return (999999, room)
    return (int(room[1:]), room)


def live_available_rooms(row: dict[str, str], room_pool: list[str], existing: list[dict[str, str]]) -> list[str]:
    available = []
    for room in room_pool:
        slots = booking_rows_for(row, room)
        if any(overlaps(slot, conflict) for slot in slots for conflict in existing):
            continue
        available.append(room)
    return sorted(available, key=room_sort_key)


def planned_conflict(row: dict[str, str], room: str, assigned_slots: list[dict[str, str]]) -> bool:
    return any(overlaps(slot, other) for slot in booking_rows_for(row, room) for other in assigned_slots)


def build_candidates(rows: list[dict[str, str]], room_pool: list[str], existing: list[dict[str, str]]) -> list[dict[str, object]]:
    candidates = []
    for row in rows:
        key = row_key(row)
        decision = USER_DECISIONS[key]
        forbidden_rooms = decision_forbidden_rooms(decision)
        allowed_rooms = decision_allowed_rooms(decision)
        available = [room for room in live_available_rooms(row, room_pool, existing) if room not in forbidden_rooms and (not allowed_rooms or room in allowed_rooms)]
        preferred_room = canonical_room(decision.get("room", ""))
        if preferred_room in NONEXISTENT_ROOMS:
            preferred_room = ""

        ordered = []
        if decision["mode"] == "use" and preferred_room:
            if preferred_room in available:
                ordered.append({"room": preferred_room, "rank": 0, "preferred": True})
            remaining = [room for room in available if room != preferred_room]
            ordered.extend(
                {"room": room, "rank": index + 1, "preferred": False}
                for index, room in enumerate(remaining)
            )
        else:
            ordered.extend(
                {"room": room, "rank": index, "preferred": False}
                for index, room in enumerate(available)
            )

        candidates.append(
            {
                "row": row,
                "key": key,
                "decision": decision,
                "preferred_room": preferred_room,
                "allowed_rooms": sorted(allowed_rooms, key=room_sort_key),
                "forbidden_rooms": sorted(forbidden_rooms, key=room_sort_key),
                "available_rooms": available,
                "ordered_candidates": ordered,
            }
        )
    return candidates


def choose_plan(items: list[dict[str, object]]) -> dict[tuple[str, str, str, str], str]:
    ordered_items = sorted(
        items,
        key=lambda item: (
            0 if item["decision"]["mode"] == "use" else 1,
            len(item["ordered_candidates"]),
            item["key"],
        ),
    )
    assignment: dict[tuple[str, str, str, str], str] = {}
    assigned_slots: list[dict[str, str]] = []

    for item in ordered_items:
        row = item["row"]
        key = item["key"]
        for candidate in item["ordered_candidates"]:
            room = candidate["room"]
            if planned_conflict(row, room, assigned_slots):
                continue
            assignment[key] = room
            assigned_slots.extend(booking_rows_for(row, room))
            break

    return assignment


def insert_assignment(session: requests.Session, rows: list[dict[str, object]], assignment: dict[tuple[str, str, str, str], str]) -> dict[str, object]:
    booking_rows = []
    for item in rows:
        key = item["key"]
        room = assignment.get(key)
        if not room:
            continue
        booking_rows.extend(booking_rows_for(item["row"], room))

    rooms = sorted({row["room"] for row in booking_rows})
    dates = sorted({row["date"] for row in booking_rows})
    existing_bookings = fetch_existing_rows(session, rooms, dates, "bookings")

    inserted = []
    skipped = []
    failed = []
    for row in booking_rows:
        payload = {
            "date": row["date"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "room": row["room"],
            "title": row["title"],
            "teacher": row["teacher"],
        }
        if exact_booking_exists(payload, existing_bookings):
            skipped.append(row)
            continue
        response = session.post(BOOKINGS_URL, json=payload, timeout=60)
        if response.status_code in (200, 201):
            inserted.append(row)
            existing_bookings.append(
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
        else:
            failed.append({"row": row, "status_code": response.status_code, "response": response.text[:500]})
    return {"inserted": inserted, "skipped": skipped, "failed": failed}


def clear_existing_assignments(session: requests.Session, rows: list[dict[str, str]]) -> int:
    cleared = 0
    for row in rows:
        for slot in slot_rows_for(row):
            params = urllib.parse.urlencode(
                {
                    "date": f"eq.{slot['date']}",
                    "start_time": f"eq.{slot['start_time']}",
                    "end_time": f"eq.{slot['end_time']}",
                    "title": f"eq.{slot['title']}",
                    "teacher": f"eq.{slot['teacher']}",
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


def build_result_rows(items: list[dict[str, object]], assignment: dict[tuple[str, str, str, str], str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    result_rows = []
    unresolved_rows = []
    for item in items:
        row = item["row"]
        decision = item["decision"]
        assigned_room = assignment.get(item["key"], "")
        preferred_room = item["preferred_room"] or ""
        available_rooms = item["available_rooms"]

        if assigned_room:
            if decision["mode"] == "use" and preferred_room == assigned_room:
                resolution = "Used requested room"
            elif decision["mode"] == "use" and preferred_room:
                resolution = f"Requested {preferred_room} could not be used globally; assigned {assigned_room} instead"
            elif decision["mode"] == "find_else":
                resolution = f"Assigned alternative room {assigned_room}"
            else:
                resolution = f"Assigned room {assigned_room}"
            status = "Assigned"
        else:
            status = "Unresolved"
            if available_rooms:
                resolution = "Live-feasible rooms exist individually, but no conflict-free global assignment could be produced with the current selections."
            else:
                resolution = "No live-feasible room was available for this course at this pass."

        result_row = {
            "course": row["course"],
            "program": row["program"],
            "block": row["block"],
            "teacher": row["teacher"],
            "decision": decision["mode"],
            "requested_room": preferred_room or "",
            "assigned_room": assigned_room or "",
            "available_room_count": str(len(available_rooms)),
            "status": status,
            "resolution": resolution,
        }
        result_rows.append(result_row)
        if status == "Unresolved":
            unresolved_rows.append(result_row)
    return result_rows, unresolved_rows


def write_table_xlsx(path: Path, title: str, rows: list[dict[str, str]], headers: list[str]) -> None:
    table = [headers] + [[row.get(header, "") for header in headers] for row in rows]
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as zf:
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
            f'<dc:title>{title}</dc:title>'
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
            '<sheets><sheet name="Results" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(table))


def write_outputs(result_rows: list[dict[str, str]], unresolved_rows: list[dict[str, str]], summary: dict[str, int]) -> str:
    headers = list(result_rows[0].keys()) if result_rows else [
        "course", "program", "block", "teacher", "decision", "requested_room", "assigned_room", "available_room_count", "status", "resolution"
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(result_rows)
    write_table_xlsx(OUT_XLSX, "Remaining 15 User Decisions", result_rows, headers)

    with UNRESOLVED_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(unresolved_rows)
    write_table_xlsx(UNRESOLVED_XLSX, "Remaining 15 User Decisions Unresolved", unresolved_rows, headers)

    payload = {"summary": summary, "rows": result_rows, "unresolved": unresolved_rows}
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        REPORT_HEADER,
        "",
        "This section applies the user's room choices for the remaining 15 rows as preferred selections, then computes a conflict-free global assignment across those rows.",
        "",
        f"- Rows reviewed: {summary['rows_reviewed']}",
        f"- Rows assigned: {summary['rows_assigned']}",
        f"- Requested rooms honored exactly: {summary['requested_rooms_honored']}",
        f"- Booking rows inserted: {summary['booking_rows_inserted']}",
        f"- Still unresolved after applying these decisions: {summary['rows_unresolved']}",
        f"- Results CSV: {OUT_CSV.name}",
        f"- Results workbook: {OUT_XLSX.name}",
        f"- Unresolved CSV: {UNRESOLVED_CSV.name}",
        f"- Unresolved workbook: {UNRESOLVED_XLSX.name}",
        "",
        "| Course | Decision | Requested room | Assigned room | Status | Resolution |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result_rows:
        lines.append(
            f"| {row['course']} | {row['decision']} | {row['requested_room'] or 'None'} | {row['assigned_room'] or 'None'} | {row['status']} | {row['resolution']} |"
        )
    lines.append("")
    text = "\n".join(lines)
    OUT_MD.write_text(text, encoding="utf-8")
    return text


def update_report(section_text: str) -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    if REPORT_HEADER in report:
        start = report.index(REPORT_HEADER)
        next_header = report.find("\n## ", start + len(REPORT_HEADER))
        if next_header == -1:
            report = report[:start].rstrip() + "\n\n" + section_text + "\n"
        else:
            report = report[:start].rstrip() + "\n\n" + section_text + "\n\n" + report[next_header + 1 :].lstrip()
    else:
        report = report.rstrip() + "\n\n" + section_text + "\n"
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> int:
    rows = load_rows()
    session = get_session()
    cleared_count = clear_existing_assignments(session, rows)
    dates = sorted({date for slots in BLOCK_SLOTS.values() for date, _, _ in slots})
    room_pool = sorted(set(fetch_room_pool(session, dates)) | set(decision_explicit_rooms()), key=room_sort_key)
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, room_pool, dates, table))

    items = build_candidates(rows, room_pool, existing)
    assignment = choose_plan(items)
    execution = insert_assignment(session, items, assignment)
    result_rows, unresolved_rows = build_result_rows(items, assignment)

    summary = {
        "rows_reviewed": len(rows),
        "rows_assigned": sum(1 for row in result_rows if row["status"] == "Assigned"),
        "requested_rooms_honored": sum(
            1
            for item in items
            if assignment.get(item["key"], "") and item["decision"]["mode"] == "use" and assignment.get(item["key"]) == item["preferred_room"]
        ),
        "prior_booking_rows_cleared": cleared_count,
        "booking_rows_inserted": len(execution["inserted"]),
        "rows_unresolved": len(unresolved_rows),
    }

    section_text = write_outputs(result_rows, unresolved_rows, summary)
    update_report(section_text)

    print(OUT_CSV)
    print(OUT_XLSX)
    print(UNRESOLVED_CSV)
    print(UNRESOLVED_XLSX)
    print(OUT_MD)
    print(OUT_JSON)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())