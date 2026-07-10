from pathlib import Path
import json


data = json.loads(Path("si_overview.json").read_text(encoding="utf-16"))

print("EXCEL FILES")
for file, sheets in data["excel"].items():
    print(f"\n{file}")
    for sheet in sheets:
        print(f"  - {sheet['sheet']}: rows={sheet['rows']} cols={sheet['cols']}")
        print(f"    first row: {sheet['columns_or_first_row'][:12]}")
        for row in sheet["head"][:2]:
            print(f"    row: {row[:12]}")

print("\nPDF FILES")
for file, info in data["pdf"].items():
    text = " ".join(info["first_text"].split())
    print(f"\n{file}")
    print(f"  pages={info['pages']}")
    print(f"  text={text[:1200]}")
