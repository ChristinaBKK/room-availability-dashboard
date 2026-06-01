#!/usr/bin/env python3
"""Generate the June 2026 schedule import TSV from the repeated timetable blocks."""

from __future__ import annotations

import csv
from pathlib import Path


OUT_PATH = Path("schedule_import_2026-06-10_to_2026-06-30.tsv")

WEDNESDAYS = ["2026/06/10", "2026/06/17", "2026/06/24"]
THURSDAYS = ["2026/06/11", "2026/06/18", "2026/06/25"]
FRIDAYS = ["2026/06/12", "2026/06/26"]
MONDAYS = ["2026/06/15", "2026/06/22", "2026/06/29"]
TUESDAYS = ["2026/06/16", "2026/06/23", "2026/06/30"]

BUSINESS_1_BLOCK = [
    ("B2039", "AS Business 1", "Mr R Hamroun"),
    ("B2041", "AS Economics 2", "Ms Z Wang"),
    ("B3002", "AS Physics 2", "Mr F Qureshi"),
    ("B3027", "11 AS Art 2", "Ms L Liu"),
    ("B3040", "11 AS Further Maths", "Ms N Magsudova"),
    ("B3042", "11 Reg Maths 2 9709 AS", "Ms J Farhat"),
    ("B4002", "G11 AS Chemistry Summit", "Ms J Zhu"),
    ("B4005", "AS Chemistry 2", "Ms F Fu"),
    ("B4029", "11 AS Art 1", "Ms A Milne"),
]

BUSINESS_2_BLOCK = [
    ("B1029", "AS Computer Sci", "Mr A Bishan"),
    ("B2039", "AS Business 2", "Ms J Jacobs-Kraft"),
    ("B2040", "11 AS Economics Summit", "Mr F Nzamy"),
    ("B3002", "AS Physics 3", "Mr F Qureshi"),
    ("B3010", "AS Economics 3", "Mr A Mugabe"),
    ("B3043", "11 Reg Maths 3 9709 AS", "Ms N Magsudova"),
    ("B4002", "AS Chemistry 3", "Ms S Sun"),
    ("B4007", "AS Biology", "Mr F Yu"),
    ("B4012", "AS Biology 2", "Ms L Hung"),
]

LS_1_BLOCK = [
    ("B2041", "AS Economics 4", "Ms C Du"),
    ("B2042", "AS Geography", "Mr A Oniango"),
    ("B3002", "11 AS Physics LS 1", "Mr S Pan"),
    ("B3004", "AS Physics 4", "Mr R Shafie"),
    ("B3039", "G11 AS Maths Learning Support", "Mr S Anwar"),
    ("B3040", "11 Reg Maths 4 9709 AS", "Ms E Wang"),
    ("B4009", "11 AL Chinese EU", "Ms J Li"),
    ("B4010", "AL Chinese 1", "Ms M Chen"),
]

LS_2_THURSDAY_BLOCK = [
    ("B2041", "AS Economics 4", "Ms C Du"),
    ("B2042", "AS Geography", "Mr A Oniango"),
    ("B3002", "11 AS Physics LS 2", "Mr S Pan"),
    ("B3004", "AS Physics 4", "Mr R Shafie"),
    ("B3040", "11 Reg Maths 4 9709 AS", "Ms E Wang"),
    ("B4009", "11 AL Chinese EU", "Ms J Li"),
    ("B4010", "AL Chinese 2", "Ms M Chen"),
    ("B4041", "11 AS Economics LS 2", "Ms Z Wang"),
]

LS_2_TUESDAY_BLOCK = [
    ("B2041", "AS Economics 4", "Ms C Du"),
    ("B2042", "AS Geography", "Mr A Oniango"),
    ("B3004", "AS Physics 4", "Mr R Shafie"),
    ("B3040", "11 Reg Maths 4 9709 AS", "Ms E Wang"),
    ("B4009", "11 AL Chinese EU", "Ms J Li"),
    ("B4010", "AL Chinese 2", "Ms M Chen"),
    ("B4041", "11 AS Economics LS 2", "Ms Z Wang"),
]

MUSIC_BLOCK_1 = [
    ("B2003", "AS Music", "Mr A Clark"),
    ("B2041", "AS Economics 1", "Ms C Du"),
    ("B3002", "AS Physics 1", "Mr C Lim"),
    ("B3027", "11 AS Art (Double)", "Mr M Ford"),
    ("B3043", "11 Reg Maths 1 9709 AS", "Ms N Magsudova"),
    ("B4005", "AS Chemistry 1", "Ms F Fu"),
]

MUSIC_BLOCK_2 = [
    ("B2003", "AS Music", "Mr A Clark"),
    ("B2041", "AS Economics 1", "Ms C Du"),
    ("B3002", "AS Physics 1", "Mr C Lim"),
    ("B3027", "11 AS Art (Double)", "Ms L Liu"),
    ("B3043", "11 Reg Maths 1 9709 AS", "Ms N Magsudova"),
    ("B4005", "AS Chemistry 1", "Ms F Fu"),
]

TUESDAY_MUSIC_BLOCK = [
    ("B2003", "AS Music", "Mr A Clark"),
    ("B2041", "AS Economics 1", "Ms C Du"),
    ("B3002", "AS Physics 1", "Mr C Lim"),
    ("B3027", "11 AS Art (Double)", "Mr M Ford"),
    ("B3043", "11 Reg Maths 1 9709 AS", "Ms N Magsudova"),
    ("B4005", "AS Chemistry 1", "Ms F Fu"),
]

FRIDAY_1435_BLOCK = [
    ("B2003", "AS Music", "Mr A Clark"),
    ("B2041", "AS Economics 1", "Ms C Du"),
    ("B3002", "AS Physics 1", "Mr C Lim"),
    ("B3043", "11 Reg Maths 1 9709 AS", "Ms N Magsudova"),
    ("B4005", "AS Chemistry 1", "Ms F Fu"),
]

FRIDAY_1520_BLOCK = [
    ("B2041", "AS Economics 1", "Ms C Du"),
    ("B3002", "AS Physics 1", "Mr C Lim"),
    ("B3043", "11 Reg Maths 1 9709 AS", "Ms N Magsudova"),
    ("B4005", "AS Chemistry 1", "Ms F Fu"),
]


def add_rows(rows: list[list[str]], dates: list[str], day: str, start: str, end: str, block: list[tuple[str, str, str]]) -> None:
    for date in dates:
        for room, course, teacher in block:
            rows.append([date, day, start, end, room, course, teacher])


def main() -> int:
    rows: list[list[str]] = []

    add_rows(rows, WEDNESDAYS, "Wednesday", "08:20", "09:00", MUSIC_BLOCK_1)
    add_rows(rows, WEDNESDAYS, "Wednesday", "09:05", "09:45", MUSIC_BLOCK_2)
    add_rows(rows, WEDNESDAYS, "Wednesday", "10:00", "10:40", LS_1_BLOCK)
    add_rows(rows, WEDNESDAYS, "Wednesday", "10:45", "11:25", LS_1_BLOCK)
    add_rows(rows, WEDNESDAYS, "Wednesday", "11:30", "12:10", BUSINESS_1_BLOCK)
    add_rows(rows, WEDNESDAYS, "Wednesday", "13:00", "13:40", BUSINESS_1_BLOCK)
    add_rows(rows, WEDNESDAYS, "Wednesday", "13:45", "14:25", BUSINESS_1_BLOCK)
    add_rows(rows, WEDNESDAYS, "Wednesday", "14:35", "15:15", BUSINESS_2_BLOCK)
    add_rows(rows, WEDNESDAYS, "Wednesday", "15:20", "16:00", BUSINESS_2_BLOCK)

    add_rows(rows, THURSDAYS, "Thursday", "08:20", "09:00", [
        ("B2039", "11G / Life Skills", "Mr A Varley"),
        ("B2041", "11E / Life Skills", "Mr D Meyer"),
        ("B2042", "11F / Life Skills", "Ms S Yuan"),
    ])
    add_rows(rows, THURSDAYS, "Thursday", "10:00", "10:40", LS_2_THURSDAY_BLOCK)
    add_rows(rows, THURSDAYS, "Thursday", "10:45", "11:25", LS_2_THURSDAY_BLOCK)
    add_rows(rows, THURSDAYS, "Thursday", "13:00", "13:40", BUSINESS_2_BLOCK)
    add_rows(rows, THURSDAYS, "Thursday", "13:45", "14:25", BUSINESS_2_BLOCK)
    add_rows(rows, THURSDAYS, "Thursday", "14:35", "15:15", BUSINESS_1_BLOCK)
    add_rows(rows, THURSDAYS, "Thursday", "15:20", "16:00", BUSINESS_1_BLOCK)

    add_rows(rows, FRIDAYS, "Friday", "10:00", "10:40", BUSINESS_1_BLOCK)
    add_rows(rows, FRIDAYS, "Friday", "10:45", "11:25", BUSINESS_1_BLOCK)
    add_rows(rows, FRIDAYS, "Friday", "11:30", "12:10", LS_1_BLOCK)
    add_rows(rows, FRIDAYS, "Friday", "14:35", "15:15", FRIDAY_1435_BLOCK)
    add_rows(rows, FRIDAYS, "Friday", "15:20", "16:00", FRIDAY_1520_BLOCK)

    add_rows(rows, MONDAYS, "Monday", "08:20", "09:00", [
        ("B2039", "11A / Life Skills", "Ms L Zhu"),
        ("B2040", "11B / Life Skills", "Mr D McQuay"),
        ("B2041", "11D / Life Skills", "Mr R Shafie"),
        ("B2042", "11C / Life Skills", "Ms S Yuan"),
    ])
    add_rows(rows, MONDAYS, "Monday", "09:05", "09:45", BUSINESS_1_BLOCK)
    add_rows(rows, MONDAYS, "Monday", "10:00", "10:40", BUSINESS_2_BLOCK)
    add_rows(rows, MONDAYS, "Monday", "10:45", "11:25", BUSINESS_2_BLOCK)
    add_rows(rows, MONDAYS, "Monday", "11:30", "12:10", LS_1_BLOCK)
    add_rows(rows, MONDAYS, "Monday", "13:00", "13:40", MUSIC_BLOCK_1)
    add_rows(rows, MONDAYS, "Monday", "13:45", "14:25", MUSIC_BLOCK_2)

    add_rows(rows, TUESDAYS, "Tuesday", "08:20", "09:00", BUSINESS_2_BLOCK)
    add_rows(rows, TUESDAYS, "Tuesday", "09:05", "09:45", BUSINESS_2_BLOCK)
    add_rows(rows, TUESDAYS, "Tuesday", "10:00", "10:40", TUESDAY_MUSIC_BLOCK)
    add_rows(rows, TUESDAYS, "Tuesday", "10:45", "11:25", TUESDAY_MUSIC_BLOCK)
    add_rows(rows, TUESDAYS, "Tuesday", "14:35", "15:15", LS_2_TUESDAY_BLOCK)
    add_rows(rows, TUESDAYS, "Tuesday", "15:20", "16:00", LS_2_TUESDAY_BLOCK)

    with OUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["Date", "Day", "Start", "End", "Room", "Course", "Teacher"])
        writer.writerows(rows)

    print(OUT_PATH)
    print(f"rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())