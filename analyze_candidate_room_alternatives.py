#!/usr/bin/env python3
"""Evaluate candidate rooms from the XLSX and append results as markdown-ready data."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import requests


SUPABASE_URL = "https://fgewwriulwdodmlbsotp.supabase.co"
SUPABASE_KEY = "sb_publishable_yvdyY62yUu7HgPw7wjy9XQ_jmcje9te"
XLSX_PATH = Path("course_room_not_feasible_and_missing_june_2026.xlsx")
OUT_PATH = Path("candidate_room_alternatives_analysis.json")
MD_OUT_PATH = Path("candidate_room_alternatives_section.md")

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}

BLOCK_SLOTS = {
    "A": [("2026/06/10", "08:20", "09:45"), ("2026/06/12", "09:05", "09:45"), ("2026/06/15", "13:00", "14:25"), ("2026/06/16", "10:00", "11:25"), ("2026/06/17", "08:20", "09:45"), ("2026/06/29", "13:00", "14:25")],
    "B": [("2026/06/10", "11:30", "14:25"), ("2026/06/11", "14:35", "16:00"), ("2026/06/12", "10:00", "11:25"), ("2026/06/15", "14:35", "16:00"), ("2026/06/17", "11:30", "14:25"), ("2026/06/18", "14:35", "16:00"), ("2026/06/29", "14:35", "16:00")],
    "B1": [("2026/06/10", "11:30", "12:10"), ("2026/06/11", "14:35", "16:00"), ("2026/06/12", "10:00", "10:40"), ("2026/06/15", "14:35", "16:00"), ("2026/06/17", "11:30", "12:10"), ("2026/06/18", "14:35", "16:00"), ("2026/06/29", "14:35", "16:00")],
    "B2": [("2026/06/10", "13:00", "14:25"), ("2026/06/17", "13:00", "14:25")],
    "C": [("2026/06/10", "14:35", "16:00"), ("2026/06/11", "13:00", "14:25"), ("2026/06/15", "10:00", "11:25"), ("2026/06/16", "08:20", "09:45"), ("2026/06/17", "14:35", "16:00"), ("2026/06/18", "13:00", "14:25"), ("2026/06/29", "10:00", "11:25")],
    "C2-TOK": [("2026/06/15", "10:00", "11:25"), ("2026/06/29", "10:00", "11:25")],
    "C2-CAS": [("2026/06/12", "10:45", "12:10")],
    "D": [("2026/06/10", "10:00", "11:25"), ("2026/06/11", "10:00", "11:25"), ("2026/06/12", "11:30", "12:10"), ("2026/06/15", "11:30", "12:10"), ("2026/06/16", "14:35", "16:00"), ("2026/06/17", "10:00", "11:25"), ("2026/06/18", "10:00", "11:25"), ("2026/06/29", "11:30", "12:10")],
    "E": [("2026/06/11", "08:20", "09:45"), ("2026/06/12", "08:20", "09:00"), ("2026/06/15", "08:20", "09:45"), ("2026/06/16", "11:30", "12:10"), ("2026/06/18", "08:20", "09:45"), ("2026/06/29", "08:20", "09:45")],
}


def normalize_room(value: str) -> str:
    room = " ".join((value or "").strip().upper().split())
    aliases = {
        "B2036 (PREFERRED)": "B2036",
        "MEETING ROOM": "B2036",
        "TOEFL TESTING ICT LAB": "B1037",
        "B-SEMINAR ROOM A": "B-Seminar Room A",
        "B SEMINAR ROOM A": "B-Seminar Room A",
    }
    return aliases.get(room, room)


def time_to_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def overlaps(a: dict[str, str], b: dict[str, str]) -> bool:
    return a["room"] == b["room"] and a["date"] == b["date"] and time_to_minutes(a["start_time"]) < time_to_minutes(b["end_time"]) and time_to_minutes(a["end_time"]) > time_to_minutes(b["start_time"])


def parse_workbook() -> list[dict[str, str]]:
    rows = []
    with ZipFile(XLSX_PATH) as zf:
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
        target = "xl/" + rel_map[rel_id]
        sheet = ET.fromstring(zf.read(target))
        headers = None
        for row in sheet.findall(".//a:sheetData/a:row", NS):
            cell_map = {}
            for cell in row.findall("a:c", NS):
                ref = cell.attrib.get("r", "")
                col = re.match(r"[A-Z]+", ref).group(0)
                value = cell.find("a:v", NS)
                if value is None:
                    text = ""
                elif cell.attrib.get("t") == "s":
                    text = shared[int(value.text)]
                else:
                    text = value.text or ""
                cell_map[col] = text
            ordered = [cell_map.get(col, "") for col in ["A", "B", "C", "D", "E", "F", "G", "H"]]
            if headers is None:
                headers = ordered
                continue
            if not any(ordered[:7]):
                continue
            rows.append(
                {
                    "course": ordered[0],
                    "program": ordered[1],
                    "block": ordered[2],
                    "teacher": ordered[3],
                    "room": ordered[4],
                    "status": ordered[5],
                    "notes": ordered[6],
                    "possible_rooms_raw": ordered[7],
                }
            )
    return rows


def candidate_rooms(raw: str) -> list[str]:
    text = (raw or "").strip()
    if not text or text.lower() == "ignore":
        return []
    if text.lower().startswith("ib theatre should be in"):
        match = re.findall(r"B\d{4}", text.upper())
        return [normalize_room(item) for item in match]
    found = re.findall(r"B(?:\d{4}(?:\s*\([^\n]+\))?|\-SEMINAR ROOM A)", text.upper())
    return [normalize_room(item) for item in found]


def fetch_existing_rows(session: requests.Session, rooms: list[str], dates: list[str], table: str) -> list[dict[str, str]]:
    rows = []
    date_filter = requests.utils.quote(
        ",".join(f"date.eq.{date}" for date in sorted(set(dates + [date.replace('/', '-') for date in dates]))),
        safe=",.=()",
    )
    for room in rooms:
        response = session.get(
            f"{SUPABASE_URL}/rest/v1/{table}?select=*&room=eq.{requests.utils.quote(room, safe='')}&or=({date_filter})&limit=1000",
            timeout=60,
        )
        response.raise_for_status()
        for row in response.json():
            rows.append(
                {
                    "source": table,
                    "date": (row.get("date") or "").replace("-", "/"),
                    "start_time": (row.get("start_time") or "").strip(),
                    "end_time": (row.get("end_time") or "").strip(),
                    "room": normalize_room(row.get("room", "")),
                    "label": (row.get("class_name") or row.get("title") or "").strip(),
                    "teacher": (row.get("teacher") or "").strip(),
                }
            )
    return rows


def summarize_blocker(candidate: dict[str, object]) -> str:
    blockers = candidate["blockers"]
    if not blockers:
        return ""
    first = blockers[0]
    return (
        f"{candidate['room']}: blocked by {first['source']} {first['conflict_time']} "
        f"{first['label']} ({first['teacher']}) on {first['date']}"
    )


def build_markdown(results: list[dict[str, object]]) -> str:
    total_courses = len(results)
    courses_with_candidates = sum(1 for item in results if item["candidate_results"])
    courses_with_feasible = sum(1 for item in results if any(candidate["feasible"] for candidate in item["candidate_results"]))
    total_candidates = sum(len(item["candidate_results"]) for item in results)
    feasible_candidates = sum(1 for item in results for candidate in item["candidate_results"] if candidate["feasible"])

    lines = [
        "## Candidate Room Feasibility From Workbook",
        "",
        "These candidate rooms were checked against the current live state in `schedule`, `bookings`, and `room_sessions`, including the June course bookings that have already been inserted.",
        "",
        "### Candidate Summary",
        "",
        f"- Blocked or missing courses reviewed from workbook: {total_courses}",
        f"- Courses with candidate rooms provided: {courses_with_candidates}",
        f"- Courses with at least one feasible candidate now: {courses_with_feasible}",
        f"- Candidate rooms checked: {total_candidates}",
        f"- Candidate rooms feasible now: {feasible_candidates}",
        f"- Courses still without a feasible candidate from the workbook: {total_courses - courses_with_feasible}",
        "",
        "### Candidate Results",
        "",
        "| Course | Program | Block | Workbook candidates | Feasible now | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for item in results:
        candidate_results = item["candidate_results"]
        all_rooms = ", ".join(candidate["room"] for candidate in candidate_results) if candidate_results else "No candidate provided"
        feasible_rooms = ", ".join(candidate["room"] for candidate in candidate_results if candidate["feasible"]) or "None"
        if not candidate_results:
            note = "Workbook entry was blank or marked ignore."
        else:
            blocked_summaries = [summarize_blocker(candidate) for candidate in candidate_results if not candidate["feasible"]]
            blocked_summaries = [summary for summary in blocked_summaries if summary]
            if feasible_rooms != "None":
                note = "Remaining blocked candidates: " + "; ".join(blocked_summaries[:2]) if blocked_summaries else "All listed candidates were feasible."
            else:
                note = "; ".join(blocked_summaries[:2]) if blocked_summaries else "No feasible candidate from workbook."
        lines.append(
            "| {course} | {program} | {block} | {candidates} | {feasible} | {note} |".format(
                course=item["course"],
                program=item["program"],
                block=item["block"],
                candidates=all_rooms.replace("|", "/"),
                feasible=feasible_rooms.replace("|", "/"),
                note=note.replace("|", "/"),
            )
        )
    lines.append("")
    lines.append("Candidate-room feasibility above is per course against the current live data. It is not yet a globally optimized room-allocation plan across the remaining blocked courses.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    workbook_rows = parse_workbook()
    relevant_rows = [row for row in workbook_rows if row["status"] == "Not Feasible"]

    all_candidate_rooms = sorted({room for row in relevant_rows for room in candidate_rooms(row["possible_rooms_raw"])})
    all_dates = sorted({date for slots in BLOCK_SLOTS.values() for date, _, _ in slots})
    session = requests.Session()
    session.headers.update({"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, all_candidate_rooms, all_dates, table))

    results = []
    for row in relevant_rows:
        candidates = candidate_rooms(row["possible_rooms_raw"])
        slots = BLOCK_SLOTS.get(row["block"], [])
        candidate_results = []
        for room in candidates:
            blockers = []
            for date, start_time, end_time in slots:
                probe = {"date": date, "start_time": start_time, "end_time": end_time, "room": room}
                conflict = next((item for item in existing if overlaps(probe, item)), None)
                if conflict:
                    blockers.append(
                        {
                            "date": date,
                            "time": f"{start_time}-{end_time}",
                            "source": conflict["source"],
                            "conflict_time": f"{conflict['start_time']}-{conflict['end_time']}",
                            "label": conflict["label"],
                            "teacher": conflict["teacher"],
                        }
                    )
            candidate_results.append(
                {
                    "room": room,
                    "feasible": not blockers,
                    "blockers": blockers,
                }
            )
        results.append(
            {
                "course": row["course"],
                "program": row["program"],
                "block": row["block"],
                "teacher": row["teacher"],
                "original_room": row["room"],
                "candidate_results": candidate_results,
            }
        )

    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    MD_OUT_PATH.write_text(build_markdown(results), encoding="utf-8")
    print(OUT_PATH)
    print(MD_OUT_PATH)
    print(json.dumps({
        "rows": len(results),
        "candidate_rooms_checked": sum(len(item["candidate_results"]) for item in results),
        "feasible_candidates": sum(1 for item in results for candidate in item["candidate_results"] if candidate["feasible"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())