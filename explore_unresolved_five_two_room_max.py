#!/usr/bin/env python3
"""Explore up-to-two-room plans for the current five unresolved rows."""

from __future__ import annotations

import csv
import itertools
import json
import os
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import requests

from analyze_candidate_room_alternatives import BLOCK_SLOTS, SUPABASE_KEY, fetch_existing_rows, normalize_room, overlaps
from export_unresolved_csv_to_xlsx import build_sheet_xml


SOURCE_CSV = Path("remaining_15_user_decisions_unresolved.csv")
OUT_CSV = Path("remaining_15_unresolved_two_room_max.csv")
OUT_XLSX = Path("remaining_15_unresolved_two_room_max.xlsx")
OUT_JSON = Path("remaining_15_unresolved_two_room_max.json")
OUT_MD = Path("remaining_15_unresolved_two_room_max.md")
REPORT_PATH = Path("course_room_feasibility_june_2026.md")
REPORT_HEADER = "## Current Unresolved 5 Two-Room Possibility"
SUPABASE_URL = "https://fgewwriulwdodmlbsotp.supabase.co"

NONEXISTENT_ROOMS = {"B2038"}
DISALLOWED_PREFIXES = {"D"}
FORBIDDEN_ROOMS = {"B-Seminar Room A", "B1011", "B1029", "B1037", "B2003", "B2004"}
ALLOWED_ROOMS = {
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
}
MAX_PATTERNS_PER_ROW = 120
ROW_ROOM_RULES = {
    ("Chinese D-1", "CIE", "D", "Miya Yang"): {
        "allowed": {"B3009", "B3010", "B3011"},
        "preferred": {"B3009"},
    },
    ("Chinese D-2", "CIE", "D", "Ivy Zhu"): {
        "allowed": {"B3009", "B3010", "B3011", "B4009", "B4010", "B4011"},
        "preferred": {"B3010"},
    },
    ("Regular Maths D", "CIE", "D", "Joy Farhat"): {
        "allowed": {"B3039", "B3040", "B3041", "B3042", "B3043"},
        "preferred": {"B3042"},
    },
    ("English E-6", "CIE", "E", "Sherry Yuan"): {
        "allowed": {"B3009", "B3010", "B3011", "B3012"},
        "preferred": {"B3012"},
    },
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
    if token in NONEXISTENT_ROOMS or token[:1] in DISALLOWED_PREFIXES:
        return ""
    room = "B-Seminar Room A" if token == "B-SEMINAR ROOM A" else token
    if room in FORBIDDEN_ROOMS:
        return ""
    return room if room in ALLOWED_ROOMS else ""


def room_sort_key(room: str) -> tuple[int, int, str]:
    if room == "B-Seminar Room A":
        return (999999, 999999, room)
    return (ord(room[0]), int(room[1:]), room)


def load_rows() -> list[dict[str, str]]:
    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["course"], row["program"], row["block"], row["teacher"])


def slot_booking(row: dict[str, str], room: str, slot_index: int) -> dict[str, str]:
    date, start_time, end_time = BLOCK_SLOTS[row["block"]][slot_index]
    return {
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "room": room,
        "title": row["course"],
        "teacher": row["teacher"],
    }


def fetch_room_pool(session: requests.Session) -> list[str]:
    rooms = set()
    for table in ("schedule", "bookings", "room_sessions"):
        offset = 0
        while True:
            response = session.get(
                f"{SUPABASE_URL}/rest/v1/{table}",
                params={"select": "room", "limit": "1000", "offset": str(offset)},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            if not payload:
                break
            for item in payload:
                room = canonical_room(item.get("room", ""))
                if room:
                    rooms.add(room)
            if len(payload) < 1000:
                break
            offset += 1000
    return sorted(rooms, key=room_sort_key)


def build_feasible_by_slot(rows: list[dict[str, str]], room_pool: list[str], existing: list[dict[str, str]]) -> dict[tuple[str, str, str, str], list[list[str]]]:
    feasible: dict[tuple[str, str, str, str], list[list[str]]] = {}
    for row in rows:
        key = row_key(row)
        rule = ROW_ROOM_RULES.get(key, {})
        allowed_rooms = rule.get("allowed", set())
        per_slot = []
        for slot_index, _ in enumerate(BLOCK_SLOTS[row["block"]]):
            available = []
            for room in room_pool:
                if allowed_rooms and room not in allowed_rooms:
                    continue
                booking = slot_booking(row, room, slot_index)
                if any(overlaps(booking, conflict) for conflict in existing):
                    continue
                available.append(room)
            per_slot.append(available)
        feasible[key] = per_slot
    return feasible


def pattern_sort_key(pattern: tuple[str, ...], preferred_rooms: set[str]) -> tuple[int, int, int, tuple[tuple[int, int, str], ...]]:
    preferred_penalty = 0 if not preferred_rooms or preferred_rooms & set(pattern) else 1
    distinct = len(set(pattern))
    changes = sum(1 for left, right in zip(pattern, pattern[1:]) if left != right)
    return (preferred_penalty, distinct, changes, tuple(room_sort_key(room) for room in pattern))


def generate_patterns(key: tuple[str, str, str, str], per_slot: list[list[str]]) -> list[tuple[str, ...]]:
    slot_count = len(per_slot)
    union_rooms = sorted({room for slot in per_slot for room in slot}, key=room_sort_key)
    patterns: set[tuple[str, ...]] = set()
    preferred_rooms = set(ROW_ROOM_RULES.get(key, {}).get("preferred", set()))

    for room in union_rooms:
        if all(room in slot for slot in per_slot):
            patterns.add(tuple(room for _ in range(slot_count)))

    for room_a, room_b in itertools.combinations(union_rooms, 2):
        if any(room_a not in slot and room_b not in slot for slot in per_slot):
            continue

        def search(slot_index: int, built: list[str]) -> None:
            if len(patterns) > MAX_PATTERNS_PER_ROW * 4:
                return
            if slot_index == slot_count:
                patterns.add(tuple(built))
                return
            candidates = []
            if room_a in per_slot[slot_index]:
                candidates.append(room_a)
            if room_b in per_slot[slot_index] and room_b != room_a:
                candidates.append(room_b)
            candidates.sort(key=lambda room: (0 if built and built[-1] == room else 1, room_sort_key(room)))
            for room in candidates:
                built.append(room)
                search(slot_index + 1, built)
                built.pop()

        search(0, [])

    sorted_patterns = sorted(patterns, key=lambda pattern: pattern_sort_key(pattern, preferred_rooms))
    two_room_patterns = [pattern for pattern in sorted_patterns if len(set(pattern)) == 2]
    if two_room_patterns:
        return two_room_patterns[:MAX_PATTERNS_PER_ROW]
    return sorted_patterns[:MAX_PATTERNS_PER_ROW]


def solve_block(rows: list[dict[str, str]], patterns_by_row: dict[tuple[str, str, str, str], list[tuple[str, ...]]]) -> tuple[set[tuple[str, str, str, str]], dict[tuple[str, str, str, str], tuple[str, ...]]]:
    best_keys: set[tuple[str, str, str, str]] = set()
    best_assignment: dict[tuple[str, str, str, str], tuple[str, ...]] = {}
    best_cost = None

    for subset_size in range(len(rows), 0, -1):
        found = False
        for subset in itertools.combinations(rows, subset_size):
            subset = list(subset)
            ordered = sorted(subset, key=lambda row: (len(patterns_by_row[row_key(row)]), row_key(row)))
            slot_count = len(BLOCK_SLOTS[ordered[0]["block"]])
            current_assignment: dict[tuple[str, str, str, str], tuple[str, ...]] = {}
            rooms_used_by_slot = [set() for _ in range(slot_count)]
            local_best = None
            local_cost = None

            def search(index: int) -> None:
                nonlocal local_best, local_cost
                if index == len(ordered):
                    cost = (
                        sum(len(set(pattern)) for pattern in current_assignment.values()),
                        sum(sum(1 for left, right in zip(pattern, pattern[1:]) if left != right) for pattern in current_assignment.values()),
                        tuple((key, current_assignment[key]) for key in sorted(current_assignment)),
                    )
                    if local_cost is None or cost < local_cost:
                        local_best = dict(current_assignment)
                        local_cost = cost
                    return

                row = ordered[index]
                key = row_key(row)
                for pattern in patterns_by_row[key]:
                    if any(pattern[slot_index] in rooms_used_by_slot[slot_index] for slot_index in range(slot_count)):
                        continue
                    for slot_index, room in enumerate(pattern):
                        rooms_used_by_slot[slot_index].add(room)
                    current_assignment[key] = pattern
                    search(index + 1)
                    current_assignment.pop(key, None)
                    for slot_index, room in enumerate(pattern):
                        rooms_used_by_slot[slot_index].remove(room)

            search(0)
            if local_best is not None:
                found = True
                solved_keys = {row_key(row) for row in subset}
                if best_cost is None or subset_size > len(best_keys) or (subset_size == len(best_keys) and local_cost < best_cost):
                    best_keys = solved_keys
                    best_assignment = local_best
                    best_cost = local_cost
        if found:
            break

    return best_keys, best_assignment


def build_output_rows(rows: list[dict[str, str]], feasibility: dict[tuple[str, str, str, str], list[list[str]]], solved_keys: set[tuple[str, str, str, str]], assignments: dict[tuple[str, str, str, str], tuple[str, ...]]) -> list[dict[str, str]]:
    output_rows = []
    for row in sorted(rows, key=lambda item: (item["block"], item["course"], item["teacher"])):
        key = row_key(row)
        if key in solved_keys:
            pattern = assignments[key]
            rooms_used = sorted(set(pattern), key=room_sort_key)
            slot_plan = "; ".join(
                f"{date} {start}-{end}={room}"
                for (date, start, end), room in zip(BLOCK_SLOTS[row["block"]], pattern)
            )
            status = "Two-room-max feasible"
            resolution = f"Uses {len(rooms_used)} room(s): {', '.join(rooms_used)}"
        else:
            rooms_used = []
            slot_plan = ""
            status = "Not solvable within 2 rooms"
            resolution = "No conflict-free assignment was found with a two-room maximum after excluding D rooms."
        feasible_summary = " | ".join(
            f"{date} {start}-{end}: {', '.join(feasibility[key][index][:5])}{' ...' if len(feasibility[key][index]) > 5 else ''}"
            for index, (date, start, end) in enumerate(BLOCK_SLOTS[row["block"]])
        )
        output_rows.append(
            {
                "course": row["course"],
                "program": row["program"],
                "block": row["block"],
                "teacher": row["teacher"],
                "status": status,
                "rooms_used": ", ".join(rooms_used),
                "slot_plan": slot_plan,
                "per_slot_feasible_sample": feasible_summary,
                "resolution": resolution,
            }
        )
    return output_rows


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
        zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>')
        zf.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>')
        zf.writestr("docProps/core.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Current Unresolved 5 Two-Room Possibility</dc:title><dc:creator>GitHub Copilot</dc:creator></cp:coreProperties>')
        zf.writestr("docProps/app.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>GitHub Copilot</Application></Properties>')
        zf.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Two Room Possibility" sheetId="1" r:id="rId1"/></sheets></workbook>')
        zf.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(table))


def write_markdown(rows: list[dict[str, str]], summary: dict[str, int]) -> str:
    lines = [
        REPORT_HEADER,
        "",
        "This section explores whether the current five unresolved rows can be covered by using up to two rooms per course across their block slots, with D rooms excluded and without changing the already assigned rows.",
        "",
        f"- Unresolved rows reviewed: {summary['rows_reviewed']}",
        f"- Rows solvable with 2-room max: {summary['rows_two_room_feasible']}",
        f"- Rows still not solvable with 2-room max: {summary['rows_still_not_feasible']}",
        f"- Analysis CSV: {OUT_CSV.name}",
        f"- Analysis workbook: {OUT_XLSX.name}",
        "",
        "| Course | Status | Rooms used | Resolution |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['course']} | {row['status']} | {row['rooms_used'] or 'None'} | {row['resolution']} |")
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
    room_pool = fetch_room_pool(session)
    dates = sorted({date for row in rows for date, _, _ in BLOCK_SLOTS[row['block']]})
    existing = []
    for table in ("schedule", "bookings", "room_sessions"):
        existing.extend(fetch_existing_rows(session, room_pool, dates, table))

    feasibility = build_feasible_by_slot(rows, room_pool, existing)
    patterns_by_row = {row_key(row): generate_patterns(row_key(row), feasibility[row_key(row)]) for row in rows}

    solved_keys: set[tuple[str, str, str, str]] = set()
    assignments: dict[tuple[str, str, str, str], tuple[str, ...]] = {}
    rows_by_block: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        rows_by_block.setdefault(row['block'], []).append(row)
    for block_rows in rows_by_block.values():
        block_solved, block_assignment = solve_block(block_rows, patterns_by_row)
        solved_keys |= block_solved
        assignments.update(block_assignment)

    output_rows = build_output_rows(rows, feasibility, solved_keys, assignments)
    summary = {
        "rows_reviewed": len(output_rows),
        "rows_two_room_feasible": sum(1 for row in output_rows if row['status'] == 'Two-room-max feasible'),
        "rows_still_not_feasible": sum(1 for row in output_rows if row['status'] != 'Two-room-max feasible'),
    }

    write_csv(output_rows)
    write_xlsx(output_rows)
    OUT_JSON.write_text(json.dumps({"summary": summary, "rows": output_rows}, indent=2), encoding="utf-8")
    section_text = write_markdown(output_rows, summary)
    update_report(section_text)

    print(OUT_CSV)
    print(OUT_XLSX)
    print(OUT_MD)
    print(OUT_JSON)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())