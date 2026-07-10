from pathlib import Path
import re

from pypdf import PdfReader


FILES = [
    Path("Xia_2024_hgcAB_SI/41467_2024_53479_MOESM1_ESM.pdf"),
    Path("Xia_2024_hgcAB_SI/41467_2024_53479_MOESM2_ESM.pdf"),
    Path("Xia_2024_hgcAB_SI/41467_2024_53479_MOESM4_ESM.pdf"),
    Path("Xia_2024_hgcAB_SI/41467_2024_53479_MOESM5_ESM.pdf"),
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
