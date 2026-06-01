#!/usr/bin/env python3
"""Export authoritative June live rooming info for the supplied course list."""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

import requests

from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, SUPABASE_URL


OUT_CSV = Path("june_2026_live_rooming_info.csv")
OUT_JSON = Path("june_2026_live_rooming_info.json")
OUT_MD = Path("june_2026_live_rooming_info.md")
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
REPORT_HEADER = "## Final June Live Rooming Info"

ALT_BOOKING_MATCHES = {
    "Physics A-1": {
        "titles": ["Physics A-1", "G10 TT Physics Block A"],
        "teachers": ["Faisal Qureshi"],
    },
    "Physics A-2 (Summit)": {
        "titles": ["Physics A-2 (Summit)", "G10 TT Physics Block A Summit"],
        "teachers": ["Faisal Qureshi"],
    },
    "Physics A-3 (EU)": {
        "titles": ["Physics A-3 (EU)", "G10 TT Physics Block A EU"],
        "teachers": ["Faisal Qureshi"],
    },
    "Physics B-1": {
        "titles": ["Physics B-1", "G10 TT Physics Block B-1"],
        "teachers": ["Faisal Qureshi"],
    },
    "Physics B-2": {
        "titles": ["Physics B-2", "G10 TT Physics Block B-2"],
        "teachers": ["Faisal Qureshi"],
    },
    "Physics D": {
        "titles": ["Physics D", "G10 TT Physics Block D"],
        "teachers": ["Faisal Qureshi"],
    },
}

COURSES = [
    {"course": "Math HL", "program": "IBDP", "block": "A", "teacher": "Rajesh Choyikkunimmal", "tid": "RJE"},
    {"course": "Math SL", "program": "IBDP", "block": "A", "teacher": "Shahid Anwar", "tid": "SAN"},
    {"course": "Regular Math A-1", "program": "CIE", "block": "A", "teacher": "Joy Farhat", "tid": "JFA"},
    {"course": "Regular Math A-2", "program": "CIE", "block": "A", "teacher": "Sheryl Shane Canite", "tid": "SCA"},
    {"course": "Physics A-1", "program": "CIE", "block": "A", "teacher": "Evelyn Yang", "tid": "EVY"},
    {"course": "Chemistry A", "program": "CIE", "block": "A", "teacher": "Selina Sun", "tid": "SSU"},
    {"course": "Economics A", "program": "CIE", "block": "A", "teacher": "Reza Hamroun", "tid": "RHA"},
    {"course": "Chinese A", "program": "CIE", "block": "A", "teacher": "Jenny Li", "tid": "JLI"},
    {"course": "Physics A-2 (Summit)", "program": "CIE", "block": "A", "teacher": "Mike Hu", "tid": "MHU"},
    {"course": "Physics A-3 (EU)", "program": "CIE", "block": "A", "teacher": "Logan Tian", "tid": "LTI"},
    {"course": "Geography", "program": "CIE", "block": "A", "teacher": "Keith Seeley / Alex Oniango", "tid": "KSL/AON"},
    {"course": "Physics B-1", "program": "CIE", "block": "B", "teacher": "Chester Lim", "tid": "CHL"},
    {"course": "Physics B-2", "program": "CIE", "block": "B", "teacher": "Evelyn Yang", "tid": "EVY"},
    {"course": "Biology", "program": "CIE", "block": "B", "teacher": "Ambily Biju", "tid": "ABI"},
    {"course": "Economics B-1", "program": "CIE", "block": "B", "teacher": "Helgaard Le Roux", "tid": "HLR"},
    {"course": "Computer Science", "program": "CIE", "block": "B", "teacher": "Bill Jiang", "tid": "BJI"},
    {"course": "Music", "program": "CIE", "block": "B", "teacher": "Andy Clark", "tid": "ACR"},
    {"course": "Chinese B", "program": "CIE", "block": "B", "teacher": "Ivy Zhu", "tid": "IZH"},
    {"course": "Economics B-2 (Summit)", "program": "CIE", "block": "B", "teacher": "Fahran Nzamy", "tid": "FNZ"},
    {"course": "Regular Maths B (EU)", "program": "CIE", "block": "B", "teacher": "Sheryl Shane Canite", "tid": "SCA"},
    {"course": "Art (Dual Dose)", "program": "CIE", "block": "B", "teacher": "Mark Ford", "tid": "MFO"},
    {"course": "Economics 2 HL/SL", "program": "IBDP", "block": "B1", "teacher": "Chaminda Marasinghe", "tid": "CMA"},
    {"course": "Biology HL/SL", "program": "IBDP", "block": "B1", "teacher": "Fisher Yu", "tid": "FYU"},
    {"course": "Theatre HL/SL", "program": "IBDP", "block": "B1", "teacher": "Chalice Rakgoale", "tid": "CRA"},
    {"course": "Physics HL/SL", "program": "IBDP", "block": "B1", "teacher": "Logan Tian", "tid": "LTI"},
    {"course": "Chinese A", "program": "IBDP", "block": "B2", "teacher": "Melody Chen", "tid": "MEC"},
    {"course": "Chinese B", "program": "IBDP", "block": "B2", "teacher": "Jenny Li/Ann Yang", "tid": "JLI"},
    {"course": "Physics HL/SL", "program": "IBDP", "block": "C", "teacher": "Logan Tian", "tid": "LTI"},
    {"course": "Chemistry HL/SL", "program": "IBDP", "block": "C", "teacher": "Judy Zhu", "tid": "ZHJ"},
    {"course": "Biology HL/SL", "program": "IBDP", "block": "C", "teacher": "Lily Hung", "tid": "LHN"},
    {"course": "Regular Math C-1", "program": "CIE", "block": "C", "teacher": "Narmina Magsudova", "tid": "NMA"},
    {"course": "Regular Math C-2", "program": "CIE", "block": "C", "teacher": "Shaun Yang", "tid": "SHY"},
    {"course": "Further Maths C", "program": "CIE", "block": "C", "teacher": "Rajesh", "tid": "RJE"},
    {"course": "Advanced Maths (CIE) C", "program": "CIE", "block": "C", "teacher": "Mandy Chen", "tid": "MCH"},
    {"course": "Chemistry C-1", "program": "CIE", "block": "C", "teacher": "Khurram Shezad", "tid": "KSH"},
    {"course": "Economics D-1", "program": "CIE", "block": "C", "teacher": "Marshall Irby", "tid": "MIR"},
    {"course": "Business", "program": "CIE", "block": "C", "teacher": "Joyce Zhou", "tid": "JZX"},
    {"course": "Chemistry C-2 (Summit)", "program": "CIE", "block": "C", "teacher": "Alistair Furze", "tid": "AFU"},
    {"course": "Economic C-2 (EU)", "program": "CIE", "block": "C", "teacher": "Winnie Hu", "tid": "WHU"},
    {"course": "TOK (Chinese)", "program": "IBDP", "block": "C2-TOK", "teacher": "Miya Yang / Matthew Peatman", "tid": "MYA/MPE"},
    {"course": "CAS", "program": "IBDP", "block": "C2-CAS", "teacher": "#N/A", "tid": "LLN"},
    {"course": "Regular Maths D", "program": "CIE", "block": "D", "teacher": "Joy Farhat", "tid": "JFA"},
    {"course": "Fast Maths (Edexcel)", "program": "CIE", "block": "D", "teacher": "Rajesh", "tid": "RJE"},
    {"course": "Advanced Math (CIE) D", "program": "CIE", "block": "D", "teacher": "Eva Wang", "tid": "WEV"},
    {"course": "Physics D", "program": "CIE", "block": "D", "teacher": "Raufie Shafie", "tid": "RSH"},
    {"course": "Chemistry D", "program": "CIE", "block": "D", "teacher": "Selina Sun", "tid": "SSU"},
    {"course": "History", "program": "CIE", "block": "D", "teacher": "Keith Seeley / Matthew Peatman", "tid": "KSL/MPE"},
    {"course": "Art", "program": "CIE", "block": "D", "teacher": "Amanda Milne / Luciana Liu", "tid": "AMM/LUL"},
    {"course": "Chinese D-1", "program": "CIE", "block": "D", "teacher": "Miya Yang", "tid": "MYA"},
    {"course": "Chinese D-2", "program": "CIE", "block": "D", "teacher": "Ivy Zhu", "tid": "IZH"},
    {"course": "English", "program": "IBDP", "block": "D", "teacher": "Warwick Midlane", "tid": "WMI"},
    {"course": "English", "program": "IBDP", "block": "D", "teacher": "Donald Meyer", "tid": "DME"},
    {"course": "English", "program": "IBDP", "block": "D", "teacher": "Darren McQuay", "tid": "DMC"},
    {"course": "Economics 1 HL/SL", "program": "IBDP", "block": "E", "teacher": "Chaminda Marasinghe", "tid": "CMA"},
    {"course": "Business H/SL", "program": "IBDP", "block": "E", "teacher": "Jennifer Jacobs-Kraft", "tid": "JJK"},
    {"course": "Philosophy H/SL", "program": "IBDP", "block": "E", "teacher": "Matthew Peatman", "tid": "MPE"},
    {"course": "English E-1", "program": "CIE", "block": "E", "teacher": "Kurt Shelton", "tid": "KUS"},
    {"course": "English E-2", "program": "CIE", "block": "E", "teacher": "Jenna Wade Dunn", "tid": "JWD"},
    {"course": "English E-3", "program": "CIE", "block": "E", "teacher": "Lim Wan", "tid": "LWA"},
    {"course": "English E-4", "program": "CIE", "block": "E", "teacher": "Helen Liu", "tid": "HLI"},
    {"course": "English E-5", "program": "CIE", "block": "E", "teacher": "Sally Guo", "tid": "SGU"},
    {"course": "English E-6", "program": "CIE", "block": "E", "teacher": "Sherry Yuan", "tid": "SYU"},
    {"course": "English E-7", "program": "CIE", "block": "E", "teacher": "Cordelia Jiao", "tid": "CJI"},
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
    session.headers.update({"apikey": key, "Authorization": f"Bearer {key}"})
    return session


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().upper())


def teacher_aliases(teacher: str) -> set[str]:
    raw = (teacher or "").strip()
    if not raw or raw == "#N/A":
        return set()
    aliases = {normalize_text(raw)}
    for part in re.split(r"/", raw):
        part = part.strip()
        if part:
            aliases.add(normalize_text(part))
    return aliases


def fetch_june_bookings(session: requests.Session) -> list[dict[str, str]]:
    rows = []
    offset = 0
    while True:
        response = session.get(
            f"{SUPABASE_URL}/rest/v1/bookings",
            params={
                "select": "date,start_time,end_time,room,title,teacher",
                "date": "gte.2026-06-01",
                "order": "date.asc,start_time.asc,title.asc",
                "limit": "1000",
                "offset": str(offset),
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload:
            break
        for row in payload:
            rows.append(
                {
                    "date": (row.get("date") or "").replace("-", "/"),
                    "start_time": (row.get("start_time") or "").strip(),
                    "end_time": (row.get("end_time") or "").strip(),
                    "room": (row.get("room") or "").strip(),
                    "title": (row.get("title") or "").strip(),
                    "teacher": (row.get("teacher") or "").strip(),
                }
            )
        if len(payload) < 1000:
            break
        offset += 1000
    return rows


def matching_rows(course: dict[str, str], bookings: list[dict[str, str]]) -> list[dict[str, str]]:
    alt_match = ALT_BOOKING_MATCHES.get(course["course"])
    if alt_match:
        title_aliases = {normalize_text(title) for title in alt_match["titles"]}
        aliases = set()
        for teacher in alt_match["teachers"]:
            aliases.update(teacher_aliases(teacher))
    else:
        title_aliases = {normalize_text(course["course"])}
        aliases = teacher_aliases(course["teacher"])

    matched = []
    for row in bookings:
        if normalize_text(row["title"]) not in title_aliases:
            continue
        row_teacher = normalize_text(row["teacher"])
        if aliases:
            if row_teacher not in aliases and not any(alias in row_teacher or row_teacher in alias for alias in aliases):
                continue
        matched.append(row)
    return matched


def summarize_course(course: dict[str, str], bookings: list[dict[str, str]]) -> dict[str, str]:
    expected_slots = BLOCK_SLOTS[course["block"]]
    matched = matching_rows(course, bookings)
    rows_by_slot = {}
    for row in matched:
        slot_key = (row["date"], row["start_time"], row["end_time"])
        rows_by_slot.setdefault(slot_key, []).append(row)

    found_rows = []
    missing_slots = []
    duplicate_slot_details = []
    for date, start_time, end_time in expected_slots:
        slot_rows = rows_by_slot.get((date, start_time, end_time), [])
        if slot_rows:
            found_rows.extend(slot_rows)
            if len(slot_rows) > 1:
                duplicate_slot_details.append(
                    f"{date} {start_time}-{end_time}=" + ", ".join(sorted({row['room'] for row in slot_rows}))
                )
        else:
            missing_slots.append(f"{date} {start_time}-{end_time}")

    rooms_used = sorted({row["room"] for row in found_rows})
    if found_rows and not missing_slots:
        status = "Booked live"
    elif found_rows:
        status = "Partially booked live"
    else:
        status = "No live booking rows found"

    if len(rooms_used) <= 1 and found_rows:
        session_details = f"Single room across booked slots: {rooms_used[0]}"
    elif found_rows:
        session_details_parts = []
        for date, start_time, end_time in expected_slots:
            slot_rows = rows_by_slot.get((date, start_time, end_time), [])
            if not slot_rows:
                continue
            rooms = ", ".join(sorted({row["room"] for row in slot_rows}))
            session_details_parts.append(f"{date} {start_time}-{end_time}={rooms}")
        session_details = "; ".join(session_details_parts)
    else:
        session_details = ""

    notes = []
    official_title = normalize_text(course["course"])
    official_teachers = teacher_aliases(course["teacher"])
    used_title_alias = any(normalize_text(row["title"]) != official_title for row in found_rows)
    used_teacher_alias = any(
        official_teachers and normalize_text(row["teacher"]) not in official_teachers
        for row in found_rows
    )
    if used_title_alias and used_teacher_alias:
        notes.append("Matched via alternate live booking title and teacher alias.")
    elif used_title_alias:
        notes.append("Matched via alternate live booking title alias.")
    elif used_teacher_alias:
        notes.append("Matched via alternate live booking teacher alias.")
    if missing_slots:
        notes.append("Missing slots: " + "; ".join(missing_slots))
    if duplicate_slot_details:
        notes.append("Duplicate live rows on slot(s): " + "; ".join(duplicate_slot_details))
    if not found_rows:
        notes.append("No matching June booking rows were found in live bookings.")

    return {
        "course": course["course"],
        "program": course["program"],
        "block": f"Block {course['block'].replace('C2-TOK', 'C2').replace('C2-CAS', 'C2')}",
        "tid": course["tid"],
        "teacher": course["teacher"],
        "status": status,
        "rooms_used": ", ".join(rooms_used) if rooms_used else "None",
        "session_details": session_details or "None",
        "notes": " ".join(notes) if notes else "All expected June slots found in live bookings.",
    }


def write_outputs(rows: list[dict[str, str]]) -> str:
    headers = ["course", "program", "block", "tid", "teacher", "status", "rooms_used", "session_details", "notes"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    OUT_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    lines = [
        REPORT_HEADER,
        "",
        "This section is the authoritative live June rooming list for the supplied course roster, built from the current `bookings` table. If a course uses more than one room, every booked session is listed explicitly.",
        "",
        f"- Courses reviewed: {len(rows)}",
        f"- Courses with all expected June slots booked live: {sum(1 for row in rows if row['status'] == 'Booked live')}",
        f"- Courses partially booked live: {sum(1 for row in rows if row['status'] == 'Partially booked live')}",
        f"- Courses with no live booking rows found: {sum(1 for row in rows if row['status'] == 'No live booking rows found')}",
        f"- CSV export: {OUT_CSV.name}",
        f"- JSON export: {OUT_JSON.name}",
        "",
        "| Course | Program | Block | TID | Teacher | Status | Rooms used | Session details | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {course} | {program} | {block} | {tid} | {teacher} | {status} | {rooms_used} | {session_details} | {notes} |".format(
                **{key: value.replace("|", "/") for key, value in row.items()}
            )
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
    session = get_session()
    bookings = fetch_june_bookings(session)
    rows = [summarize_course(course, bookings) for course in COURSES]
    section_text = write_outputs(rows)
    update_report(section_text)
    print(OUT_CSV)
    print(OUT_JSON)
    print(OUT_MD)
    print(json.dumps({
        "courses_reviewed": len(rows),
        "booked_live": sum(1 for row in rows if row["status"] == "Booked live"),
        "partially_booked_live": sum(1 for row in rows if row["status"] == "Partially booked live"),
        "no_live_booking_rows_found": sum(1 for row in rows if row["status"] == "No live booking rows found"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())