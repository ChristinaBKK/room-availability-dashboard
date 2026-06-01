#!/usr/bin/env python3
"""Explore whether the five unresolved rows can be covered with up to two rooms per course."""

from __future__ import annotations

import csv
import json
from itertools import combinations
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

import requests

from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, SUPABASE_URL, fetch_existing_rows, normalize_room, overlaps
from export_unresolved_csv_to_xlsx import build_sheet_xml


UNRESOLVED_CSV = Path("remaining_15_user_decisions_unresolved.csv")
OPTIONS_CSV = Path("remaining_15_unresolved_live_options.csv")
OUT_CSV = Path("remaining_15_unresolved_two_room_exploration.csv")
OUT_XLSX = Path("remaining_15_unresolved_two_room_exploration.xlsx")
OUT_JSON = Path("remaining_15_unresolved_two_room_exploration.json")
OUT_MD = Path("remaining_15_unresolved_two_room_exploration.md")
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
REPORT_HEADER = "## Current Unresolved 5 Two-Room Exploration"


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"})
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


def row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["course"], row["program"], row["block"], row["teacher"])


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def fetch_existing(session: requests.Session, rooms: list[str], dates: list[str]) -> list[dict[str, str]]:
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, rooms, dates, table))
    return existing


def candidate_rooms_map() -> dict[tuple[str, str, str, str], list[str]]:
    options_rows = load_csv_rows(OPTIONS_CSV)
    mapping = {}
    for row in options_rows:
        rooms = [canonical_room(item) for item in row["best_live_feasible_rooms"].split(",")]
        mapping[row_key(row)] = [room for room in rooms if room]
    return mapping


def slot_feasible(row: dict[str, str], slot_index: int, room: str, existing: list[dict[str, str]]) -> bool:
    slot = booking_rows_for(row, room)[slot_index]
    return not any(overlaps(slot, conflict) for conflict in existing)


def attempt_block_plan(rows: list[dict[str, str]], allowed: dict[tuple[str, str, str, str], list[str]], existing: list[dict[str, str]]) -> dict[str, object] | None:
    slots = list(range(len(BLOCK_SLOTS[rows[0]["block"]])))
    feasible_by_row = {}
    for row in rows:
        key = row_key(row)
        feasible_by_row[key] = []
        for slot_index in slots:
            candidates = [room for room in allowed[key] if slot_feasible(row, slot_index, room, existing)]
            if not candidates:
                return None
            feasible_by_row[key].append(candidates)

    best_plan = None
    best_score = None

    def search_slot(slot_index: int, used_by_row: dict[tuple[str, str, str, str], tuple[str, ...]], assignments: dict[tuple[str, str, str, str], list[str]]) -> None:
        nonlocal best_plan, best_score
        if slot_index == len(slots):
            changes = sum(
                1
                for row in rows
                for idx in range(1, len(assignments[row_key(row)]))
                if assignments[row_key(row)][idx] != assignments[row_key(row)][idx - 1]
            )
            total_rooms = sum(len(set(assignments[row_key(row)])) for row in rows)
            score = (changes, total_rooms)
            if best_score is None or score < best_score:
                best_score = score
                best_plan = {key: value[:] for key, value in assignments.items()}
            return

        room_in_slot: set[str] = set()
        slot_assignments: dict[tuple[str, str, str, str], str] = {}
        ordered_rows = sorted(rows, key=lambda row: len(feasible_by_row[row_key(row)][slot_index]))

        def assign_row(index: int) -> None:
            if index == len(ordered_rows):
                next_used = dict(used_by_row)
                next_assignments = {key: value[:] for key, value in assignments.items()}
                for key, room in slot_assignments.items():
                    if room not in next_used[key]:
                        next_used[key] = tuple(sorted(set(next_used[key]) | {room}, key=room_sort_key))
                    next_assignments[key].append(room)
                search_slot(slot_index + 1, next_used, next_assignments)
                return

            row = ordered_rows[index]
            key = row_key(row)
            candidates = []
            for room in feasible_by_row[key][slot_index]:
                if room in room_in_slot:
                    continue
                current_rooms = set(used_by_row[key])
                if room not in current_rooms and len(current_rooms) >= 2:
                    continue
                candidates.append(room)
            candidates.sort(key=lambda room: (0 if room in used_by_row[key] else 1, room_sort_key(room)))
            for room in candidates:
                room_in_slot.add(room)
                slot_assignments[key] = room
                assign_row(index + 1)
                slot_assignments.pop(key, None)
                room_in_slot.remove(room)

        assign_row(0)

    initial_used = {row_key(row): tuple() for row in rows}
    initial_assignments = {row_key(row): [] for row in rows}
    search_slot(0, initial_used, initial_assignments)
    if best_plan is None:
        return None

    return {
        "assignments": best_plan,
        "rooms_used": {key: sorted(set(value), key=room_sort_key) for key, value in best_plan.items()},
        "score": best_score,
    }


def best_block_solution(rows: list[dict[str, str]], allowed: dict[tuple[str, str, str, str], list[str]], existing: list[dict[str, str]]) -> dict[str, object]:
    row_keys = [row_key(row) for row in rows]
    for size in range(len(rows), 0, -1):
        subset_solutions = []
        for subset in combinations(rows, size):
            plan = attempt_block_plan(list(subset), allowed, existing)
            if plan is not None:
                subset_solutions.append((subset, plan))
        if subset_solutions:
            subset, plan = min(subset_solutions, key=lambda item: item[1]["score"])
            solved_keys = {row_key(row) for row in subset}
            return {
                "solved_keys": solved_keys,
                "unsolved_keys": [key for key in row_keys if key not in solved_keys],
                "plan": plan,
            }
    return {"solved_keys": set(), "unsolved_keys": row_keys, "plan": None}


def write_outputs(result_rows: list[dict[str, str]], summary: dict[str, object]) -> str:
    headers = list(result_rows[0].keys()) if result_rows else []
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(result_rows)

    table = [headers] + [[row.get(header, "") for header in headers] for row in result_rows]
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
            '<dc:title>Remaining 5 Two Room Exploration</dc:title>'
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
            '<sheets><sheet name="Two Room Exploration" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(table))

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        REPORT_HEADER,
        "",
        "This section explores whether the current five unresolved rows can be covered by allowing each course to use up to 2 rooms across its block slots.",
        "",
        f"- Rows reviewed: {summary['rows_reviewed']}",
        f"- Rows solvable with 2-room max: {summary['rows_solved']}",
        f"- Rows still not solvable with 2-room max: {summary['rows_unsolved']}",
        f"- Results CSV: {OUT_CSV.name}",
        f"- Results workbook: {OUT_XLSX.name}",
        "",
        "| Course | Block | Status | Rooms used | Slot-by-slot plan |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result_rows:
        lines.append(
            f"| {row['course']} | {row['block']} | {row['status']} | {row['rooms_used'] or 'None'} | {row['slot_plan'] or row['notes']} |"
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
    unresolved_rows = load_csv_rows(UNRESOLVED_CSV)
    allowed_map = candidate_rooms_map()
    session = get_session()
    rooms = sorted({room for rooms in allowed_map.values() for room in rooms}, key=room_sort_key)
    dates = sorted({date for row in unresolved_rows for date, _, _ in BLOCK_SLOTS[row['block']]})
    existing = fetch_existing(session, rooms, dates)

    summary = {"rows_reviewed": len(unresolved_rows), "blocks": {}}
    result_rows = []
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in unresolved_rows:
        grouped.setdefault(row["block"], []).append(row)

    for block, rows in sorted(grouped.items()):
        solution = best_block_solution(rows, allowed_map, existing)
        plan = solution["plan"]
        summary["blocks"][block] = {
            "solved_courses": sorted([" / ".join(key) for key in solution["solved_keys"]]),
            "unsolved_courses": sorted([" / ".join(key) for key in solution["unsolved_keys"]]),
        }
        if plan is not None:
            for key in solution["solved_keys"]:
                row = next(item for item in rows if row_key(item) == key)
                assignments = plan["assignments"][key]
                slot_plan = "; ".join(
                    f"{date} {start_time}-{end_time}={room}"
                    for (date, start_time, end_time), room in zip(BLOCK_SLOTS[block], assignments)
                )
                result_rows.append(
                    {
                        "course": row["course"],
                        "program": row["program"],
                        "block": block,
                        "teacher": row["teacher"],
                        "status": "Solvable with 2-room max",
                        "rooms_used": ", ".join(plan["rooms_used"][key]),
                        "slot_plan": slot_plan,
                        "notes": "",
                    }
                )
        for key in solution["unsolved_keys"]:
            row = next(item for item in rows if row_key(item) == key)
            result_rows.append(
                {
                    "course": row["course"],
                    "program": row["program"],
                    "block": block,
                    "teacher": row["teacher"],
                    "status": "Still not solvable with 2-room max",
                    "rooms_used": "",
                    "slot_plan": "",
                    "notes": "No conflict-free assignment was found even when allowing up to 2 rooms across this course's slots.",
                }
            )

    result_rows.sort(key=lambda row: (row["block"], row["course"], row["teacher"]))
    summary["rows_solved"] = sum(1 for row in result_rows if row["status"] == "Solvable with 2-room max")
    summary["rows_unsolved"] = sum(1 for row in result_rows if row["status"] != "Solvable with 2-room max")

    section_text = write_outputs(result_rows, summary)
    update_report(section_text)

    print(OUT_CSV)
    print(OUT_XLSX)
    print(OUT_MD)
    print(OUT_JSON)
    print(json.dumps({"rows_reviewed": summary["rows_reviewed"], "rows_solved": summary["rows_solved"], "rows_unsolved": summary["rows_unsolved"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())