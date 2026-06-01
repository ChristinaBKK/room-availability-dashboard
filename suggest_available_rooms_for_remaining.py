#!/usr/bin/env python3
"""Suggest live-available rooms for the remaining blocked June rows."""

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
from export_unresolved_csv_to_xlsx import build_sheet_xml


SOURCE_CSV = Path("candidate_room_remaining_blocked_results.csv")
OUT_CSV = Path("candidate_room_remaining_blocked_suggestions.csv")
OUT_XLSX = Path("candidate_room_remaining_blocked_suggestions.xlsx")
OUT_JSON = Path("candidate_room_remaining_blocked_suggestions.json")
OUT_MD = Path("candidate_room_remaining_blocked_suggestions.md")
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
REPORT_HEADER = "## Remaining 15 Suggested Available Rooms"


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


def booking_rows_for(course: dict[str, str], room: str) -> list[dict[str, str]]:
    return [
        {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "room": canonical_room(room),
            "title": course["course"],
            "teacher": course["teacher"],
            "program": course["program"],
            "block": course["block"],
        }
        for date, start_time, end_time in BLOCK_SLOTS[course["block"]]
    ]


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
        for row in response.json():
            room = canonical_room(row.get("room", ""))
            if room:
                rooms.add(room)
    return sorted(rooms)


def room_sort_key(room: str) -> tuple[int, str]:
    if room == "B-Seminar Room A":
        return (999999, room)
    return (int(room[1:]), room)


def summarize_blocker(blockers: list[dict[str, str]]) -> str:
    if not blockers:
        return ""
    first = blockers[0]
    return (
        f"{first['room']} blocked by {first['source']} {first['start_time']}-{first['end_time']} "
        f"{first['label']} ({first['teacher']}) on {first['date']}"
    )


def build_suggestions(rows: list[dict[str, str]], rooms: list[str], existing: list[dict[str, str]]) -> list[dict[str, str]]:
    suggestions = []
    for row in rows:
        course = {key: row[key] for key in ("course", "program", "block", "teacher")}
        available = []
        blocked = []
        for room in rooms:
            blockers = []
            for booking in booking_rows_for(course, room):
                for conflict in existing:
                    if overlaps(booking, conflict):
                        blockers.append(
                            {
                                "room": room,
                                "date": booking["date"],
                                "source": conflict["source"],
                                "start_time": conflict["start_time"],
                                "end_time": conflict["end_time"],
                                "label": conflict["label"],
                                "teacher": conflict["teacher"],
                            }
                        )
                        break
            if blockers:
                blocked.append(blockers)
            else:
                available.append(room)

        available = sorted(available, key=room_sort_key)
        suggestions.append(
            {
                "course": row["course"],
                "program": row["program"],
                "block": row["block"],
                "teacher": row["teacher"],
                "request": row["request"],
                "current_blocker_summary": row["action_outcome"],
                "suggested_available_rooms": ", ".join(available[:12]) or "None found",
                "available_room_count": str(len(available)),
                "first_blocked_example": summarize_blocker(blocked[0]) if blocked else "",
            }
        )
    return suggestions


def write_csv(rows: list[dict[str, str]]) -> None:
    headers = list(rows[0].keys()) if rows else [
        "course",
        "program",
        "block",
        "teacher",
        "request",
        "current_blocker_summary",
        "suggested_available_rooms",
        "available_room_count",
        "first_blocked_example",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(rows: list[dict[str, str]]) -> None:
    headers = list(rows[0].keys()) if rows else [
        "course",
        "program",
        "block",
        "teacher",
        "request",
        "current_blocker_summary",
        "suggested_available_rooms",
        "available_room_count",
        "first_blocked_example",
    ]
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
            '<dc:title>Remaining Blocked Room Suggestions</dc:title>'
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
            '<sheets><sheet name="Room Suggestions" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(table))


def write_markdown(rows: list[dict[str, str]]) -> str:
    lines = [
        REPORT_HEADER,
        "",
        "This section suggests rooms that are fully available across all slots for each of the remaining 15 blocked courses, based on the current live state in `schedule`, `bookings`, and `room_sessions`.",
        "",
        f"- Remaining blocked rows reviewed: {len(rows)}",
        f"- Suggestions export: {OUT_CSV.name}",
        f"- Suggestions workbook: {OUT_XLSX.name}",
        "",
        "| Course | Block | Suggested available rooms | Count |",
        "| --- | --- | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['course']} | {row['block']} | {row['suggested_available_rooms']} | {row['available_room_count']} |"
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
    dates = sorted({date for slots in BLOCK_SLOTS.values() for date, _, _ in slots})
    rooms = fetch_room_pool(session, dates)
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, rooms, dates, table))

    suggestions = build_suggestions(rows, rooms, existing)
    write_csv(suggestions)
    write_xlsx(suggestions)
    OUT_JSON.write_text(json.dumps({"rooms_scanned": len(rooms), "rows": suggestions}, indent=2), encoding="utf-8")
    section_text = write_markdown(suggestions)
    update_report(section_text)
    print(OUT_CSV)
    print(OUT_XLSX)
    print(OUT_MD)
    print(OUT_JSON)
    print({"rows": len(suggestions), "rooms_scanned": len(rooms)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())