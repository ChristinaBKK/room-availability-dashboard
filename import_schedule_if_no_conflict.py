#!/usr/bin/env python3
"""Import schedule rows into Supabase only when they do not overlap existing rows."""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime
from pathlib import Path

import requests


DEFAULT_SUPABASE_URL = "https://fgewwriulwdodmlbsotp.supabase.co"
SCHEDULE_COLUMNS = ("date", "start_time", "end_time", "class_name", "room", "teacher")
CLASS_NAME_ALIASES = {
    "ADVANCED MATH C (CIE)": "Advanced Maths (CIE) C",
}


def get_supabase_config() -> tuple[str, str]:
    supabase_url = os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL)
    supabase_key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
    )
    if not supabase_key:
        raise RuntimeError(
            "Missing Supabase API key. Set SUPABASE_SERVICE_ROLE_KEY, SERVICE_ROLE_KEY, SUPABASE_KEY, or SUPABASE_ANON_KEY."
        )
    return supabase_url, supabase_key


def normalize_room(value: str) -> str:
    room = (value or "").strip().upper()
    aliases = {
        "MEETING ROOM": "B2036",
        "TOEFL TESTING ICT LAB": "B1037",
        "B-SEMINAR ROOM A": "B-Seminar Room A",
        "B SEMINAR ROOM A": "B-Seminar Room A",
    }
    return aliases.get(room, room)


def normalize_class_name(value: str) -> str:
    class_name = (value or "").strip()
    if not class_name:
        return ""
    return CLASS_NAME_ALIASES.get(class_name.upper(), class_name)


def normalize_date(value: str) -> str:
    value = (value or "").strip().replace("-", "/")
    if not value:
        return ""
    if len(value) >= 10 and value[4] == "/":
        return value[:10]
    return datetime.strptime(value, "%d/%m/%Y").strftime("%Y/%m/%d")


def time_to_minutes(value: str) -> int:
    hours, minutes = (value or "").strip().split(":")
    return int(hours) * 60 + int(minutes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", type=Path, help="TSV file with Date/Day/Start/End/Room/Course/Teacher columns")
    parser.add_argument("--report-prefix", default="schedule_import", help="Prefix for generated report files")
    parser.add_argument("--expected-count", type=int, default=None, help="Optional expected input row count")
    parser.add_argument("--batch-size", type=int, default=100, help="Insert batch size")
    parser.add_argument("--dry-run", action="store_true", help="Do not insert rows; only produce the conflict report")
    return parser.parse_args()


def load_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        candidates = []
        for row in reader:
            if not row.get("Date"):
                continue
            candidates.append(
                {
                    "date": normalize_date(row["Date"]),
                    "start_time": row["Start"].strip(),
                    "end_time": row["End"].strip(),
                    "class_name": normalize_class_name(row["Course"]),
                    "room": normalize_room(row["Room"]),
                    "teacher": row["Teacher"].strip(),
                    "source_day": row["Day"].strip(),
                }
            )
    return candidates


def build_room_date_queries(candidates: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    rooms = sorted({item["room"] for item in candidates})
    date_tokens = []
    for date_value in sorted({item["date"] for item in candidates}):
        date_tokens.append(date_value)
        date_tokens.append(date_value.replace("/", "-"))
    return rooms, sorted(set(date_tokens))


def fetch_existing_rows(
    session: requests.Session,
    rooms: list[str],
    date_tokens: list[str],
    table_name: str,
) -> list[dict[str, str]]:
    supabase_url, _ = get_supabase_config()
    rows: list[dict[str, str]] = []
    or_filter = ",".join(f"date.eq.{token}" for token in date_tokens)
    encoded_or_filter = requests.utils.quote(or_filter, safe=",.=()")

    for room in rooms:
        offset = 0
        while True:
            params = (
                f"select=*"
                f"&room=eq.{requests.utils.quote(room, safe='')}"
                f"&or=({encoded_or_filter})"
                f"&limit=1000&offset={offset}"
            )
            response = session.get(f"{supabase_url}/rest/v1/{table_name}?{params}", timeout=60)
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break

            for row in batch:
                rows.append(
                    {
                        "source": table_name,
                        "id": row.get("id"),
                        "date": normalize_date(row.get("date", "")),
                        "start_time": (row.get("start_time") or "").strip(),
                        "end_time": (row.get("end_time") or "").strip(),
                        "room": normalize_room(row.get("room", "")),
                        "label": row.get("class_name") or row.get("title") or "",
                        "teacher": row.get("teacher") or "",
                    }
                )

            if len(batch) < 1000:
                break
            offset += 1000

    return rows


def find_conflicts(
    candidates: list[dict[str, str]],
    existing: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    accepted: list[dict[str, str]] = []
    conflicts: list[dict[str, object]] = []
    pool = list(existing)

    for index, session in enumerate(candidates, start=1):
        start_minutes = time_to_minutes(session["start_time"])
        end_minutes = time_to_minutes(session["end_time"])
        overlapping = []

        for other in pool:
            if other["room"] != session["room"] or other["date"] != session["date"]:
                continue
            if start_minutes < time_to_minutes(other["end_time"]) and end_minutes > time_to_minutes(other["start_time"]):
                overlapping.append(other)

        if overlapping:
            conflicts.append({"index": index, "session": session, "conflicts": overlapping})
            continue

        accepted.append(session)
        pool.append(
            {
                "source": "accepted_batch",
                "id": None,
                "date": session["date"],
                "start_time": session["start_time"],
                "end_time": session["end_time"],
                "room": session["room"],
                "label": session["class_name"],
                "teacher": session["teacher"],
            }
        )

    return accepted, conflicts


def insert_rows(
    session: requests.Session,
    rows: list[dict[str, str]],
    batch_size: int,
) -> list[dict[str, object]]:
    supabase_url, _ = get_supabase_config()
    failures: list[dict[str, object]] = []
    total_batches = (len(rows) + batch_size - 1) // batch_size if rows else 0
    for batch_index, batch_start in enumerate(range(0, len(rows), batch_size), start=1):
        batch = rows[batch_start : batch_start + batch_size]
        payload_batch = [{column: row[column] for column in SCHEDULE_COLUMNS} for row in batch]
        print(f"Posting batch {batch_index}/{total_batches} with {len(batch)} rows...", flush=True)
        response = session.post(f"{supabase_url}/rest/v1/schedule", json=payload_batch, timeout=60)
        if response.status_code in (200, 201):
            print(f"Batch {batch_index}/{total_batches} inserted.", flush=True)
            continue

        print(
            f"Batch {batch_index}/{total_batches} failed with status {response.status_code}; retrying row-by-row.",
            flush=True,
        )
        for row in batch:
            payload_row = {column: row[column] for column in SCHEDULE_COLUMNS}
            item_response = session.post(f"{supabase_url}/rest/v1/schedule", json=payload_row, timeout=60)
            if item_response.status_code in (200, 201):
                continue
            failures.append(
                {
                    "session": row,
                    "status_code": item_response.status_code,
                    "response": item_response.text[:500],
                }
            )

    return failures


def write_reports(
    root: Path,
    prefix: str,
    summary: dict[str, object],
    conflicts: list[dict[str, object]],
    insert_failures: list[dict[str, object]],
) -> tuple[Path, Path]:
    json_path = root / f"{prefix}_report.json"
    csv_path = root / f"{prefix}_conflicts.csv"

    json_path.write_text(
        json.dumps(
            {
                "summary": summary,
                "conflicts": conflicts,
                "insert_failures": insert_failures,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "session_index",
                "date",
                "start_time",
                "end_time",
                "room",
                "class_name",
                "teacher",
                "conflict_source",
                "conflict_id",
                "conflict_start_time",
                "conflict_end_time",
                "conflict_label",
                "conflict_teacher",
            ]
        )
        for item in conflicts:
            session = item["session"]
            for clash in item["conflicts"]:
                writer.writerow(
                    [
                        item["index"],
                        session["date"],
                        session["start_time"],
                        session["end_time"],
                        session["room"],
                        session["class_name"],
                        session["teacher"],
                        clash["source"],
                        clash["id"],
                        clash["start_time"],
                        clash["end_time"],
                        clash["label"],
                        clash["teacher"],
                    ]
                )

    return json_path, csv_path


def main() -> int:
    args = parse_args()
    candidates = load_candidates(args.input_file)
    rooms, date_tokens = build_room_date_queries(candidates)
    _, supabase_key = get_supabase_config()

    session = requests.Session()
    session.headers.update(
        {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
    )

    existing = []
    for table_name in ("room_sessions", "schedule", "bookings"):
        existing.extend(fetch_existing_rows(session, rooms, date_tokens, table_name))

    accepted, conflicts = find_conflicts(candidates, existing)
    insert_failures: list[dict[str, object]] = []
    if not args.dry_run:
        insert_failures = insert_rows(session, accepted, args.batch_size)

    inserted_count = len(accepted) - len(insert_failures) if not args.dry_run else 0
    summary = {
        "expected_sessions": args.expected_count,
        "parsed_sessions": len(candidates),
        "expected_count_matches": args.expected_count is None or len(candidates) == args.expected_count,
        "preexisting_rows_considered": len(existing),
        "non_conflicting_sessions": len(accepted),
        "conflicting_sessions": len(conflicts),
        "inserted_sessions": inserted_count,
        "insert_failures": len(insert_failures),
        "dry_run": args.dry_run,
    }

    json_path, csv_path = write_reports(args.input_file.parent, args.report_prefix, summary, conflicts, insert_failures)
    print(json.dumps(summary, indent=2))
    print(f"json_report={json_path}")
    print(f"csv_report={csv_path}")
    for item in conflicts[:15]:
        session_row = item["session"]
        clash = item["conflicts"][0]
        print(
            f"conflict #{item['index']}: {session_row['date']} {session_row['start_time']}-{session_row['end_time']} "
            f"{session_row['room']} {session_row['class_name']} -> {clash['source']} "
            f"{clash['start_time']}-{clash['end_time']} {clash['label']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())