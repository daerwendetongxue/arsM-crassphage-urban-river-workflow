from pathlib import Path
import re

from pypdf import PdfReader


FILES = [
    Path("supplementary_files/metadata_text_1.pdf"),
    Path("supplementary_files/metadata_text_2.pdf"),
    Path("supplementary_files/metadata_text_3.pdf"),
    Path("supplementary_files/metadata_text_4.pdf"),
]

OUT_DIR = Path("si_text")
OUT_DIR.mkdir(exist_ok=True)

for path in FILES:
    reader = PdfReader(str(path))
    parts = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = re.sub(r"\n{3,}", "\n\n", text)
        parts.append(f"\n===== PAGE {i} =====\n{text}")
    out = OUT_DIR / f"{path.stem}.txt"
    out.write_text("".join(parts), encoding="utf-8")
    print(f"{out} pages={len(reader.pages)} chars={out.stat().st_size}")
