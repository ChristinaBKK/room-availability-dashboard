#!/usr/bin/env python3
"""Dump worksheet rows from the candidate-room workbook."""

from __future__ import annotations

import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


DEFAULT_PATH = Path("course_room_not_feasible_and_missing_june_2026.xlsx")
NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    with ZipFile(path) as zf:
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for item in root.findall("a:si", NS):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//a:t", NS)))

        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        relationships = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}

        for sheet in workbook.findall("a:sheets/a:sheet", NS):
            print(f"SHEET\t{sheet.attrib['name']}")
            rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = "xl/" + rel_map[rel_id]
            sheet_root = ET.fromstring(zf.read(target))
            for row in sheet_root.findall(".//a:sheetData/a:row", NS):
                values = []
                for cell in row.findall("a:c", NS):
                    value = cell.find("a:v", NS)
                    if value is None:
                        values.append("")
                        continue
                    if cell.attrib.get("t") == "s":
                        values.append(shared_strings[int(value.text)])
                    else:
                        values.append(value.text or "")
                print("\t".join(values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())