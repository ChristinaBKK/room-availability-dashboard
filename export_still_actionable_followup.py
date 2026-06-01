#!/usr/bin/env python3
"""Export only the still-actionable follow-up rows to CSV and XLSX."""

from __future__ import annotations

import csv
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from export_unresolved_csv_to_xlsx import build_sheet_xml


SOURCE_CSV = Path("candidate_room_request_followup.csv")
OUT_CSV = Path("candidate_room_still_actionable.csv")
OUT_XLSX = Path("candidate_room_still_actionable.xlsx")


def load_rows() -> list[dict[str, str]]:
    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def filter_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("action_status") != "Verified already covered"]


def write_csv(rows: list[dict[str, str]]) -> None:
    if not rows:
        headers = [
            "course",
            "program",
            "block",
            "teacher",
            "request",
            "current_feasible_candidates",
            "action_status",
            "action_outcome",
            "booked_now",
        ]
    else:
        headers = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(rows: list[dict[str, str]]) -> None:
    table = []
    headers = list(rows[0].keys()) if rows else [
        "course",
        "program",
        "block",
        "teacher",
        "request",
        "current_feasible_candidates",
        "action_status",
        "action_outcome",
        "booked_now",
    ]
    table.append(headers)
    table.extend([[row.get(header, "") for header in headers] for row in rows])

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
            '<dc:title>Candidate Room Still Actionable</dc:title>'
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
            '<sheets><sheet name="Still Actionable" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        zf.writestr("xl/worksheets/sheet1.xml", build_sheet_xml(table))


def main() -> int:
    rows = filter_rows(load_rows())
    write_csv(rows)
    write_xlsx(rows)
    print(OUT_CSV)
    print(OUT_XLSX)
    print({"rows": len(rows)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())