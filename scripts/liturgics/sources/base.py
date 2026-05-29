from __future__ import annotations

import hashlib
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from liturgics.models import PageRange


def page_side(physical_page: int) -> str:
    """Return 'recto' (front) for odd pages, 'verso' (back) for even pages."""
    return "recto" if physical_page % 2 == 1 else "verso"


def slice_pdf(source_path: Path, page_range: PageRange | None, output_path: Path) -> int:
    reader = PdfReader(str(source_path))
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError(f"PDF has no pages: {source_path}")

    start = page_range.start if page_range and page_range.start is not None else 1
    end = page_range.end if page_range and page_range.end is not None else total_pages

    if start > total_pages:
        raise ValueError(
            f"Pages.Start ({start}) exceeds page count ({total_pages}) in {source_path}"
        )
    if end > total_pages:
        raise ValueError(
            f"Pages.End ({end}) exceeds page count ({total_pages}) in {source_path}"
        )

    writer = PdfWriter()
    for page_index in range(start - 1, end):
        writer.add_page(reader.pages[page_index])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        writer.write(handle)

    return end - start + 1


def cache_key(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return digest
