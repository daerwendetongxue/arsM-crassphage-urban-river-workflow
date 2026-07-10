from pathlib import Path
import json
import re
import zipfile
import xml.etree.ElementTree as ET

from pypdf import PdfReader


EXCEL_FILES = [
    Path("supplementary_files/source_data.xlsx"),
    Path("supplementary_files/sample_metadata.xlsx"),
]

PDF_FILES = [
    Path("supplementary_files/metadata_text_1.pdf"),
    Path("supplementary_files/metadata_text_2.pdf"),
    Path("supplementary_files/metadata_text_3.pdf"),
    Path("supplementary_files/metadata_text_4.pdf"),
]


def inspect_excel(path: Path) -> list[dict]:
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }

    def col_idx(cell_ref: str) -> int:
        letters = re.sub(r"[^A-Z]", "", cell_ref.upper())
        value = 0
        for ch in letters:
            value = value * 26 + ord(ch) - 64
        return value - 1

    def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
        try:
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
        except KeyError:
            return []
        strings = []
        for si in root.findall("main:si", ns):
            parts = [t.text or "" for t in si.findall(".//main:t", ns)]
            strings.append("".join(parts))
        return strings

    def cell_value(cell: ET.Element, shared: list[str]) -> str:
        cell_type = cell.attrib.get("t")
        if cell_type == "inlineStr":
            return "".join(t.text or "" for t in cell.findall(".//main:t", ns))
        value = cell.find("main:v", ns)
        if value is None or value.text is None:
            return ""
        raw = value.text
        if cell_type == "s":
            try:
                return shared[int(raw)]
            except (ValueError, IndexError):
                return raw
        return raw

    with zipfile.ZipFile(path) as zf:
        shared = load_shared_strings(zf)
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("pkgrel:Relationship", ns)
        }
        sheet_refs = []
        for sheet in workbook.findall("main:sheets/main:sheet", ns):
            name = sheet.attrib["name"]
            rid = sheet.attrib[f"{{{ns['rel']}}}id"]
            target = rel_map[rid].replace("\\", "/")
            if not target.startswith("xl/"):
                target = "xl/" + target.lstrip("/")
            sheet_refs.append((name, target))

        sheets = []
        for sheet_name, target in sheet_refs:
            root = ET.fromstring(zf.read(target))
            rows = []
            max_col = 0
            for row in root.findall("main:sheetData/main:row", ns):
                values = {}
                for cell in row.findall("main:c", ns):
                    ref = cell.attrib.get("r", "")
                    idx = col_idx(ref) if ref else len(values)
                    values[idx] = cell_value(cell, shared)
                    max_col = max(max_col, idx + 1)
                if values:
                    rows.append(values)
            dense_rows = []
            for values in rows[:5]:
                dense_rows.append([values.get(i, "") for i in range(min(max_col, 20))])
            header = dense_rows[0] if dense_rows else []
            sheets.append(
                {
                    "sheet": sheet_name,
                    "rows": len(rows),
                    "cols": max_col,
                    "columns_or_first_row": header,
                    "head": dense_rows[1:4],
                }
            )
        return sheets


def inspect_pdf(path: Path) -> dict:
    reader = PdfReader(str(path))
    first_pages = "\n".join((page.extract_text() or "") for page in reader.pages[:3])
    return {"pages": len(reader.pages), "first_text": first_pages[:5000]}


result = {
    "excel": {str(path): inspect_excel(path) for path in EXCEL_FILES},
    "pdf": {str(path): inspect_pdf(path) for path in PDF_FILES},
}

print(json.dumps(result, ensure_ascii=False, indent=2))
