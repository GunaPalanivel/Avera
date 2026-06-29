#!/usr/bin/env python3
"""Export docs/submission/deck.md to docs/submission/deck.pdf for portal upload."""

import re
from pathlib import Path

from fpdf import FPDF

REPO = Path(__file__).resolve().parents[1]
DECK_MD = REPO / "docs" / "submission" / "deck.md"
DECK_PDF = REPO / "docs" / "submission" / "deck.pdf"


class DeckPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 8, "Avera - Redrob Track 1", align="R")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def normalize_text(text: str) -> str:
    """Replace Unicode punctuation so core Helvetica fonts work."""
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2192": "->",
        "\u00d7": "x",
        "\u201c": '"',
        "\u201d": '"',
        "\u2019": "'",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("ascii", "replace").decode("ascii")


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return normalize_text(text.strip())


def write_slide(pdf: DeckPDF, body: str) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)
    for line in body.splitlines():
        line = strip_md(line)
        if not line:
            pdf.ln(4)
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            line = "  |  ".join(cells)
        pdf.multi_cell(0, 6, line)
        pdf.ln(1)


def main() -> None:
    raw = DECK_MD.read_text(encoding="utf-8")
    slides = [s.strip() for s in raw.split("\n---\n") if s.strip()]
    pdf = DeckPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    for slide in slides:
        write_slide(pdf, slide)
    DECK_PDF.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(DECK_PDF))
    print(f"Wrote {DECK_PDF}")


if __name__ == "__main__":
    main()
