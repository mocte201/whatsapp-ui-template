#!/usr/bin/env python3
"""Extract embedded text from PDFs in corpus/. Does not OCR. Stdlib + optional pypdf."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"


def extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        print(
            "pypdf no está instalado. Instalálo o copiá el texto del visor a un .txt.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def main() -> int:
    pdfs = sorted(CORPUS.rglob("*.pdf"))
    if not pdfs:
        print("No hay PDF en corpus/. Copiá ejemplos ahí (ver corpus/README.md).")
        return 0
    n = 0
    for pdf in pdfs:
        text = extract_pdf(pdf)
        out = pdf.with_suffix(".txt")
        out.write_text(text, encoding="utf-8")
        status = "ok" if text.strip() else "scan_sin_texto"
        print("{0}\t{1}\t{2} chars".format(status, pdf.relative_to(CORPUS), len(text)))
        n += 1
    print("wrote {0} .txt next to PDFs (gitignored)".format(n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
