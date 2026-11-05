"""Stage 1: extract PDF, HTML, Markdown, and text sources page by page."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from .models import Document, Page


class _HTMLText(HTMLParser):
    """Keep block boundaries and serialize table rows as pipe-delimited cells."""

    BLOCKS = {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"}:
            self.cell = []
        elif tag in self.BLOCKS and self.row is None:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.cell is not None:
            if self.row is not None:
                self.row.append(" ".join(self.cell))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.parts.extend([" | ".join(self.row), "\n"])
            self.row = None
        elif tag in self.BLOCKS and self.row is None:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            if self.cell is not None:
                self.cell.append(cleaned)
            else:
                self.parts.append(cleaned)


def _markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        _, marker, remainder = text.partition("\n---")
        if marker:
            text = remainder.partition("\n")[2]
    return text


def _pdf(path: Path) -> list[tuple[str, bool]]:
    import pdfplumber
    import pytesseract
    from pdf2image import convert_from_path

    pages: list[tuple[str, bool]] = []
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(layout=False) or ""
            if len(re.sub(r"\s+", "", text)) < 25:
                images = convert_from_path(str(path), first_page=number, last_page=number, dpi=250)
                text = pytesseract.image_to_string(images[0]) if images else ""
                pages.append((text, True))
            else:
                tables = page.extract_tables() or []
                if tables:
                    rendered = []
                    for table in tables:
                        for row in table:
                            cells = [" ".join((cell or "").split()) for cell in row]
                            rendered.append(" | ".join(cells))
                    text = f"{text}\n\n[Extracted table rows]\n" + "\n".join(rendered)
                pages.append((text, False))
    return pages


def extract(path: str, doc_version: str, superseded: bool) -> Document:
    """Extract page text and OCR individual PDF pages with no useful text layer."""
    source_path = Path(path)
    suffix = source_path.suffix.lower()
    if suffix == ".pdf":
        extracted = _pdf(source_path)
    elif suffix in {".html", ".htm"}:
        parser = _HTMLText()
        parser.feed(source_path.read_text(encoding="utf-8", errors="replace"))
        extracted = [("\n".join(parser.parts), False)]
    elif suffix == ".md":
        extracted = [(_markdown(source_path), False)]
    elif suffix == ".txt":
        extracted = [(source_path.read_text(encoding="utf-8", errors="replace"), False)]
    else:
        raise ValueError(f"unsupported document format: {source_path.suffix}")
    return Document(
        source=source_path.name,
        doc_version=doc_version,
        superseded=superseded,
        pages=[Page(source_path.name, i, text, ocr) for i, (text, ocr) in enumerate(extracted, 1)],
    )
