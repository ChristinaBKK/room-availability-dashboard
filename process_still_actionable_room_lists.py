#!/usr/bin/env python3
"""Process column J room lists from the still-actionable workbook."""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

import requests

from allocate_candidate_rooms_june_2026 import exact_booking_exists
from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, fetch_existing_rows, normalize_room, overlaps
from export_unresolved_csv_to_xlsx import build_sheet_xml


WORKBOOK_PATH = Path(os.getenv("ROOM_RETRY_WORKBOOK", "candidate_room_still_actionable.xlsx"))
ANALYSIS_JSON = Path(os.getenv("ROOM_RETRY_ANALYSIS_JSON", "candidate_room_still_actionable_actions.json"))
FOLLOWUP_CSV = Path(os.getenv("ROOM_RETRY_RESULTS_CSV", "candidate_room_still_actionable_results.csv"))
FOLLOWUP_XLSX = Path(os.getenv("ROOM_RETRY_RESULTS_XLSX", "candidate_room_still_actionable_results.xlsx"))
SECTION_MD = Path(os.getenv("ROOM_RETRY_SECTION_MD", "candidate_room_still_actionable_results.md"))
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
REPORT_SECTION_HEADER = os.getenv("ROOM_RETRY_REPORT_HEADER", "## Column J Room Retry")
SECTION_DESCRIPTION = os.getenv(
    "ROOM_RETRY_SECTION_DESCRIPTION",
    "This section records the recheck against the room lists added in column J of the still-actionable workbook.",
)

NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BOOKINGS_URL = "https://fgewwriulwdodmlbsotp.supabase.co/rest/v1/bookings"


def parse_workbook() -> list[dict[str, str]]:
    rows = []
    with ZipFile(WORKBOOK_PATH) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for item in root.findall("a:si", NS):
                shared.append("".join(node.text or "" for node in item.findall(".//a:t", NS)))

        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        first_sheet = workbook.find("a:sheets/a:sheet", NS)
        rel_id = first_sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        sheet = ET.fromstring(zf.read("xl/" + rel_map[rel_id]))

        for row in sheet.findall(".//a:sheetData/a:row", NS):
            row_number = int(row.attrib.get("r", "0"))
            if row_number == 1:
                continue
            cell_map = {}
            for cell in row.findall("a:c", NS):
                ref = cell.attrib.get("r", "")
                match = re.match(r"[A-Z]+", ref)
                if not match:
                    continue
                column = match.group(0)
                value = cell.find("a:v", NS)
                if value is None:
                    text = ""
                elif cell.attrib.get("t") == "s":
                    text = shared[int(value.text)]
                else:
                    text = value.text or ""
                cell_map[column] = text

            ordered = [cell_map.get(column, "") for column in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]]
            if not any(ordered):
                continue
            rows.append(
                {
                    "course": ordered[0],
                    "program": ordered[1],
                    "block": ordered[2],
                    "teacher": ordered[3],
                    "request": ordered[4],
                    "current_feasible_candidates": ordered[5],
                    "action_status": ordered[6],
                    "action_outcome": ordered[7],
                    "booked_now": ordered[8],
                    "room_list": ordered[9],
                }
            )
    return rows


def parse_candidate_rooms(raw: str) -> list[str]:
    rooms = []
    seen = set()
    for match in re.findall(r"B(?:\d{4}|\-SEMINAR ROOM A)", (raw or "").upper()):
        room = normalize_room(match)
        if room not in seen:
            seen.add(room)
            rooms.append(room)
    return rooms


def booking_rows_for(course: dict[str, str], room: str) -> list[dict[str, str]]:
    return [
        {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "room": normalize_room(room),
            "title": course["course"],
            "teacher": course["teacher"],
            "program": course["program"],
            "block": course["block"],
        }
        for date, start_time, end_time in BLOCK_SLOTS[course["block"]]
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


def summarize_blockers(blockers: list[dict[str, str]]) -> str:
    if not blockers:
        return ""
    parts = []
    seen = set()
    for blocker in blockers:
        key = (blocker["room"], blocker["label"], blocker["teacher"], blocker["date"], blocker["start_time"], blocker["end_time"])
        if key in seen:
            continue
        seen.add(key)
        parts.append(
            f"{blocker['room']} blocked by {blocker['source']} {blocker['start_time']}-{blocker['end_time']} {blocker['label']} ({blocker['teacher']}) on {blocker['date']}"
        )
        if len(parts) == 3:
            break
    return "; ".join(parts)


def build_xlsx(rows: list[list[str]]) -> None:
    with ZipFile(FOLLOWUP_XLSX, "w", compression=ZIP_DEFLATED) as zf:
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
            '<dc:title>Still Actionable Room List Results</dc:title>'
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
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(rows))


def update_report(section_text: str) -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    header = REPORT_SECTION_HEADER
    if header in report:
        start = report.index(header)
        next_header = report.find("\n## ", start + len(header))
        if next_header == -1:
            report = report[:start].rstrip() + "\n\n" + section_text + "\n"
        else:
            report = report[:start].rstrip() + "\n\n" + section_text + "\n\n" + report[next_header + 1 :].lstrip()
    else:
        report = report.rstrip() + "\n\n" + section_text + "\n"
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> int:
    request_rows = parse_workbook()
    session = get_session()

    rooms = sorted({room for row in request_rows for room in parse_candidate_rooms(row["room_list"])})
    dates = sorted({date for slots in BLOCK_SLOTS.values() for date, _, _ in slots})
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, rooms, dates, table))

    result_rows = []
    additional_bookings = []

    for row in request_rows:
        course = {key: row[key] for key in ("course", "program", "block", "teacher")}
        candidate_rooms = parse_candidate_rooms(row["room_list"])
        feasible_rooms = []
        blocked_rooms = []

        for room in candidate_rooms:
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
                blocked_rooms.append({"room": room, "blockers": blockers})
            else:
                feasible_rooms.append(room)

        status = "Still blocked"
        chosen_room = ""
        booked_now = "No"
        outcome = summarize_blockers([blocker for item in blocked_rooms for blocker in item["blockers"]]) or row["action_outcome"]

        if feasible_rooms:
            chosen_room = feasible_rooms[0]
            bookable_rows = booking_rows_for(course, chosen_room)
            if all(not exact_booking_exists(item, existing) for item in bookable_rows):
                for item in bookable_rows:
                    response = session.post(
                        BOOKINGS_URL,
                        json={
                            "date": item["date"],
                            "start_time": item["start_time"],
                            "end_time": item["end_time"],
                            "room": item["room"],
                            "title": item["title"],
                            "teacher": item["teacher"],
                        },
                        timeout=60,
                    )
                    response.raise_for_status()
                    existing.append(
                        {
                            "source": "bookings",
                            "date": item["date"],
                            "start_time": item["start_time"],
                            "end_time": item["end_time"],
                            "room": item["room"],
                            "label": item["title"],
                            "teacher": item["teacher"],
                        }
                    )
                additional_bookings.extend(bookable_rows)
                status = "Booked now"
                booked_now = "Yes"
                outcome = f"Booked in {chosen_room} across {len(bookable_rows)} slot(s)."
            else:
                status = "Already present"
                outcome = f"Bookings already exist in {chosen_room}."

        result_rows.append(
            {
                "course": row["course"],
                "program": row["program"],
                "block": row["block"],
                "teacher": row["teacher"],
                "request": row["request"],
                "listed_rooms": ", ".join(candidate_rooms) or "None",
                "feasible_rooms": ", ".join(feasible_rooms) or "None",
                "chosen_room": chosen_room or "None",
                "action_status": status,
                "action_outcome": outcome,
                "booked_now": booked_now,
            }
        )

    with FOLLOWUP_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "course",
                "program",
                "block",
                "teacher",
                "request",
                "listed_rooms",
                "feasible_rooms",
                "chosen_room",
                "action_status",
                "action_outcome",
                "booked_now",
            ],
        )
        writer.writeheader()
        writer.writerows(result_rows)

    build_xlsx([
        [
            "course",
            "program",
            "block",
            "teacher",
            "request",
            "listed_rooms",
            "feasible_rooms",
            "chosen_room",
            "action_status",
            "action_outcome",
            "booked_now",
        ]
    ] + [[
        row["course"],
        row["program"],
        row["block"],
        row["teacher"],
        row["request"],
        row["listed_rooms"],
        row["feasible_rooms"],
        row["chosen_room"],
        row["action_status"],
        row["action_outcome"],
        row["booked_now"],
    ] for row in result_rows])

    summary = {
        "rows_processed": len(result_rows),
        "courses_booked": len({(row["title"], row["teacher"]) for row in additional_bookings}),
        "booking_rows_inserted": len(additional_bookings),
        "still_blocked": sum(1 for row in result_rows if row["action_status"] == "Still blocked"),
        "already_present": sum(1 for row in result_rows if row["action_status"] == "Already present"),
        "booked_now": sum(1 for row in result_rows if row["action_status"] == "Booked now"),
    }
    ANALYSIS_JSON.write_text(json.dumps({"summary": summary, "rows": result_rows}, indent=2), encoding="utf-8")

    section_lines = [
        REPORT_SECTION_HEADER,
        "",
        SECTION_DESCRIPTION,
        "",
        f"- Rows processed: {summary['rows_processed']}",
        f"- Courses booked now: {summary['booked_now']}",
        f"- Booking rows inserted: {summary['booking_rows_inserted']}",
        f"- Still blocked: {summary['still_blocked']}",
        f"- Already present: {summary['already_present']}",
        f"- Results CSV: {FOLLOWUP_CSV.name}",
        f"- Results workbook: {FOLLOWUP_XLSX.name}",
        "",
        "| Course | Listed rooms | Feasible now | Outcome |",
        "| --- | --- | --- | --- |",
    ]
    for row in result_rows:
        section_lines.append(
            f"| {row['course']} | {row['listed_rooms']} | {row['feasible_rooms']} | {row['action_status']}: {row['action_outcome']} |"
        )
    section_lines.append("")
    section_text = "\n".join(section_lines)
    SECTION_MD.write_text(section_text, encoding="utf-8")
    update_report(section_text)

    print(ANALYSIS_JSON)
    print(FOLLOWUP_CSV)
    print(FOLLOWUP_XLSX)
    print(SECTION_MD)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())