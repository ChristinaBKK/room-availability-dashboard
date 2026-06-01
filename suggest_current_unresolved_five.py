#!/usr/bin/env python3
"""Suggest live-feasible rooms for the current five unresolved rows."""

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


SOURCE_CSV = Path("remaining_15_user_decisions_results.csv")
OUT_CSV = Path("remaining_15_unresolved_live_options.csv")
OUT_XLSX = Path("remaining_15_unresolved_live_options.xlsx")
OUT_JSON = Path("remaining_15_unresolved_live_options.json")
OUT_MD = Path("remaining_15_unresolved_live_options.md")
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
REPORT_HEADER = "## Current Unresolved 5 Live-Feasible Rooms"
DISALLOWED_ROOM_PREFIXES = {"D"}
PROBE_ROOMS = {
    ("Regular Maths D", "CIE", "D", "Joy Farhat"): ["B3042"],
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
    match = re.search(r"[A-Z]\d{4}|B-SEMINAR ROOM A", text.upper())
    if not match:
        return ""
    token = match.group(0)
    return "B-Seminar Room A" if token == "B-SEMINAR ROOM A" else token


def row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["course"], row["program"], row["block"], row["teacher"])


def load_rows() -> list[dict[str, str]]:
    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row["status"] == "Unresolved"]


def booking_rows_for(row: dict[str, str], room: str) -> list[dict[str, str]]:
    return [
        {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "room": canonical_room(room),
            "title": row["course"],
            "teacher": row["teacher"],
        }
        for date, start_time, end_time in BLOCK_SLOTS[row["block"]]
    ]


def room_sort_key(room: str) -> tuple[int, str]:
    if room == "B-Seminar Room A":
        return (999999, room)
    return (int(room[1:]), room)


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
    return sorted(rooms, key=room_sort_key)


def build_rows(rows: list[dict[str, str]], room_pool: list[str], existing: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        available = []
        for room in room_pool:
            if room[:1] in DISALLOWED_ROOM_PREFIXES:
                continue
            slots = booking_rows_for(row, room)
            if any(overlaps(slot, conflict) for slot in slots for conflict in existing):
                continue
            available.append(room)

        key = row_key(row)
        probes = []
        for room in PROBE_ROOMS.get(key, []):
            canonical = canonical_room(room)
            probes.append(f"{canonical}:{'yes' if canonical in available else 'no'}")

        output.append(
            {
                "course": row["course"],
                "program": row["program"],
                "block": row["block"],
                "teacher": row["teacher"],
                "available_room_count": str(len(available)),
                "best_live_feasible_rooms": ", ".join(available[:15]) or "None found",
                "probe_results": ", ".join(probes) or "",
            }
        )
    return output


def write_csv(rows: list[dict[str, str]]) -> None:
    headers = list(rows[0].keys()) if rows else [
        "course", "program", "block", "teacher", "available_room_count", "best_live_feasible_rooms", "probe_results"
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(rows: list[dict[str, str]]) -> None:
    headers = list(rows[0].keys()) if rows else [
        "course", "program", "block", "teacher", "available_room_count", "best_live_feasible_rooms", "probe_results"
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
            '<dc:title>Current Unresolved 5 Live Feasible Rooms</dc:title>'
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
            '<sheets><sheet name="Unresolved Options" sheetId="1" r:id="rId1"/></sheets></workbook>',
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
        "This section lists the best remaining live-feasible rooms for the current five unresolved rows after the latest constrained assignment pass.",
        "",
        f"- Unresolved rows reviewed: {len(rows)}",
        f"- Suggestions CSV: {OUT_CSV.name}",
        f"- Suggestions workbook: {OUT_XLSX.name}",
        "",
        "| Course | Block | Best live-feasible rooms | Count | Probe |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['course']} | {row['block']} | {row['best_live_feasible_rooms']} | {row['available_room_count']} | {row['probe_results'] or 'None'} |"
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
    room_pool = fetch_room_pool(session, dates)
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, room_pool, dates, table))

    suggestion_rows = build_rows(rows, room_pool, existing)
    write_csv(suggestion_rows)
    write_xlsx(suggestion_rows)
    OUT_JSON.write_text(json.dumps(suggestion_rows, indent=2), encoding="utf-8")
    section_text = write_markdown(suggestion_rows)
    update_report(section_text)

    print(OUT_CSV)
    print(OUT_XLSX)
    print(OUT_MD)
    print(OUT_JSON)
    print(json.dumps({"rows": len(suggestion_rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())