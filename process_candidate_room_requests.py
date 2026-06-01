#!/usr/bin/env python3
"""Process action requests added to the unresolved candidate-room workbook."""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import requests

from allocate_candidate_rooms_june_2026 import exact_booking_exists
from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, fetch_existing_rows, normalize_room, overlaps
from export_unresolved_csv_to_xlsx import build_sheet_xml


WORKBOOK_PATH = Path("candidate_room_unresolved_after_plan.xlsx")
ORIGINAL_UNRESOLVED_CSV = Path("course_room_not_feasible_and_missing_june_2026.csv")
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
ANALYSIS_JSON = Path("candidate_room_request_actions.json")
FOLLOWUP_CSV = Path("candidate_room_request_followup.csv")
FOLLOWUP_XLSX = Path("candidate_room_request_followup.xlsx")
SECTION_MD = Path("candidate_room_request_followup_section.md")

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}


def parse_request_workbook() -> list[dict[str, str]]:
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
        headers = None
        for row in sheet.findall(".//a:sheetData/a:row", NS):
            cell_map = {}
            for cell in row.findall("a:c", NS):
                ref = cell.attrib.get("r", "")
                column = re.match(r"[A-Z]+", ref).group(0)
                value = cell.find("a:v", NS)
                if value is None:
                    text = ""
                elif cell.attrib.get("t") == "s":
                    text = shared[int(value.text)]
                else:
                    text = value.text or ""
                cell_map[column] = text
            ordered = [cell_map.get(column, "") for column in ["A", "B", "C", "D", "E", "F", "G"]]
            if headers is None:
                headers = ordered
                continue
            if not any(ordered):
                continue
            rows.append(
                {
                    "course": ordered[0],
                    "program": ordered[1],
                    "block": ordered[2],
                    "teacher": ordered[3],
                    "workbook_candidates": ordered[4],
                    "reason": ordered[5],
                    "request": ordered[6],
                }
            )
    return rows


def parse_original_rooms() -> dict[tuple[str, str, str, str], str]:
    result = {}
    with ORIGINAL_UNRESOLVED_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            result[(row["course"], row["program"], row["block"], row["teacher"])] = row["room"]
    return result


def parse_plan_rows() -> list[dict[str, str]]:
    text = REPORT_PATH.read_text(encoding="utf-8")
    start = text.index("### Planned Allocations\n")
    end = text.index("\n### Still Unresolved After Global Allocation\n", start)
    rows = []
    for line in text[start:end].splitlines():
        line = line.strip()
        if not line.startswith("|") or "Chosen room" in line or line.startswith("| ---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 7:
            continue
        rows.append(
            {
                "course": parts[0],
                "program": parts[1],
                "block": parts[2],
                "teacher": parts[3],
                "room": parts[4],
            }
        )
    return rows


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


def parse_candidate_rooms(raw: str) -> list[str]:
    return [normalize_room(match) for match in re.findall(r"B(?:\d{4}|\-SEMINAR ROOM A)", (raw or "").upper())]


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


def summarize_blockers(blockers: list[dict[str, str]], plan_keys: set[tuple[str, str]]) -> str:
    if not blockers:
        return ""
    parts = []
    seen = set()
    for blocker in blockers:
        key = (blocker["room"], blocker["label"], blocker["teacher"], blocker["date"])
        if key in seen:
            continue
        seen.add(key)
        kind = "current booked candidate allocation" if (blocker["label"], blocker["teacher"]) in plan_keys else blocker["source"]
        parts.append(
            f"{blocker['room']} blocked by {kind} {blocker['conflict_time']} {blocker['label']} ({blocker['teacher']}) on {blocker['date']}"
        )
        if len(parts) == 2:
            break
    return "; ".join(parts)


def create_followup_xlsx() -> None:
    with FOLLOWUP_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.reader(handle)]
    with ZipFile(FOLLOWUP_XLSX, "w") as zf:
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
            '<dc:title>Candidate Room Request Followup</dc:title>'
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
            '<sheets><sheet name="Followup" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(rows))


def main() -> int:
    request_rows = parse_request_workbook()
    original_rooms = parse_original_rooms()
    plan_rows = parse_plan_rows()
    plan_keys = {(row["course"], row["teacher"]) for row in plan_rows}
    plan_booking_rows = [booking for row in plan_rows for booking in booking_rows_for(row, row["room"])]

    session = get_session()
    rooms = set()
    for row in request_rows:
        rooms.update(parse_candidate_rooms(row["workbook_candidates"]))
        original_room = original_rooms.get((row["course"], row["program"], row["block"], row["teacher"]))
        if original_room:
            rooms.add(original_room)
    rooms = sorted(rooms)
    dates = sorted({date for slots in BLOCK_SLOTS.values() for date, _, _ in slots})
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, rooms, dates, table))

    followup_rows = []
    additional_bookings = []
    for row in request_rows:
        course = {key: row[key] for key in ("course", "program", "block", "teacher")}
        candidates = parse_candidate_rooms(row["workbook_candidates"])
        current_feasible = []
        current_blocked = []
        for room in candidates:
            blockers = []
            for booking in booking_rows_for(course, room):
                for conflict in existing:
                    if overlaps(booking, conflict):
                        blockers.append(
                            {
                                "room": room,
                                "date": booking["date"],
                                "source": conflict["source"],
                                "conflict_time": f"{conflict['start_time']}-{conflict['end_time']}",
                                "label": conflict["label"],
                                "teacher": conflict["teacher"],
                            }
                        )
                        break
            if blockers:
                current_blocked.append({"room": room, "blockers": blockers})
            else:
                current_feasible.append(room)

        request_lower = row["request"].lower()
        status = "No action"
        outcome = row["reason"]
        booked_now = "No"

        if "already booked" in request_lower or "double-check" in request_lower:
            original_room = original_rooms.get((row["course"], row["program"], row["block"], row["teacher"]), "")
            overlapping_existing = []
            for booking in booking_rows_for(course, original_room):
                for conflict in existing:
                    if overlaps({**booking, "title": row["course"]}, conflict) and conflict["source"] == "bookings":
                        overlapping_existing.append(conflict)
                        break
            if overlapping_existing:
                status = "Verified already covered"
                outcome = summarize_blockers(
                    [
                        {
                            "room": normalize_room(original_room),
                            "date": item["date"],
                            "source": item["source"],
                            "conflict_time": f"{item['start_time']}-{item['end_time']}",
                            "label": item["label"],
                            "teacher": item["teacher"],
                        }
                        for item in overlapping_existing
                    ],
                    plan_keys,
                )
            else:
                status = "Needs manual check"
                outcome = "No overlapping existing booking was found in the original room for these slots."
        elif "try other rooms" in request_lower:
            if current_feasible:
                bookable_rows = booking_rows_for(course, current_feasible[0])
                if all(not exact_booking_exists(item, existing) for item in bookable_rows):
                    for item in bookable_rows:
                        response = session.post(
                            "https://fgewwriulwdodmlbsotp.supabase.co/rest/v1/bookings",
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
                    outcome = f"Booked in {current_feasible[0]} across {len(bookable_rows)} slot(s)."
                else:
                    status = "Already present"
                    outcome = f"Bookings already exist in {current_feasible[0]}."
            else:
                status = "Still blocked"
                outcome = summarize_blockers(
                    [blocker for item in current_blocked for blocker in item["blockers"]],
                    plan_keys,
                ) or row["reason"]
        elif "give detail" in request_lower:
            status = "Detailed explanation added"
            if current_feasible:
                outcome = f"Would be feasible in {', '.join(current_feasible)}, but those rooms are not part of the fixed booked allocation set check recorded earlier."
            else:
                outcome = summarize_blockers(
                    [blocker for item in current_blocked for blocker in item["blockers"]],
                    plan_keys,
                ) or row["reason"]

        followup_rows.append(
            {
                "course": row["course"],
                "program": row["program"],
                "block": row["block"],
                "teacher": row["teacher"],
                "request": row["request"],
                "current_feasible_candidates": ", ".join(current_feasible) or "None",
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
                "current_feasible_candidates",
                "action_status",
                "action_outcome",
                "booked_now",
            ],
        )
        writer.writeheader()
        writer.writerows(followup_rows)
    create_followup_xlsx()

    section_lines = [
        "## Request Follow-Up",
        "",
        "This section records the actions requested in column G of the unresolved workbook and the outcome after rechecking the live state with the current booked candidate allocations left in place.",
        "",
        f"- Requests processed: {len(followup_rows)}",
        f"- Additional rows booked from these requests: {len(additional_bookings)}",
        f"- Additional courses booked from these requests: {len({(row['title'], row['teacher']) for row in additional_bookings})}",
        f"- Follow-up export: {FOLLOWUP_CSV.name}",
        f"- Follow-up workbook: {FOLLOWUP_XLSX.name}",
        "",
        "| Course | Request | Feasible now | Outcome |",
        "| --- | --- | --- | --- |",
    ]
    for row in followup_rows:
        section_lines.append(
            f"| {row['course']} | {row['request']} | {row['current_feasible_candidates']} | {row['action_status']}: {row['action_outcome']} |"
        )
    section_lines.append("")
    SECTION_MD.write_text("\n".join(section_lines), encoding="utf-8")

    payload = {
        "requests_processed": len(followup_rows),
        "additional_booking_rows": len(additional_bookings),
        "additional_courses_booked": len({(row['title'], row['teacher']) for row in additional_bookings}),
        "followup_rows": followup_rows,
    }
    ANALYSIS_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(ANALYSIS_JSON)
    print(FOLLOWUP_CSV)
    print(FOLLOWUP_XLSX)
    print(SECTION_MD)
    print(json.dumps({
        "requests_processed": payload["requests_processed"],
        "additional_booking_rows": payload["additional_booking_rows"],
        "additional_courses_booked": payload["additional_courses_booked"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())