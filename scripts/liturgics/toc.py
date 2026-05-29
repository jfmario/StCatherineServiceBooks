from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from liturgics.fonts import BODY_FONT, TITLE_FONT
from liturgics.models import TocEntry


LINES_PER_PAGE = 40
LEFT_MARGIN = 1 * inch
RIGHT_MARGIN = 1 * inch
TOP_MARGIN = 1 * inch
LINE_HEIGHT = 14


def _draw_toc_page(
    pdf: canvas.Canvas,
    entries: list[TocEntry],
    page_index: int,
    page_width: float,
    page_height: float,
) -> None:
    start = page_index * LINES_PER_PAGE
    end = start + LINES_PER_PAGE
    page_entries = entries[start:end]

    y = page_height - TOP_MARGIN
    if page_index == 0:
        pdf.setFont(TITLE_FONT, 18)
        pdf.drawString(LEFT_MARGIN, y, "Contents")
        y -= LINE_HEIGHT * 2

    pdf.setFont(BODY_FONT, 12)
    usable_width = page_width - LEFT_MARGIN - RIGHT_MARGIN

    for entry in page_entries:
        title = entry.name
        page_label = str(entry.printed_page)
        title_width = pdf.stringWidth(title, BODY_FONT, 12)
        page_width_text = pdf.stringWidth(page_label, BODY_FONT, 12)
        dot_width = pdf.stringWidth(".", BODY_FONT, 12)
        gap = usable_width - title_width - page_width_text
        dot_count = max(2, int(gap / dot_width))
        line = f"{title}{'.' * dot_count}{page_label}"
        pdf.drawString(LEFT_MARGIN, y, line)
        y -= LINE_HEIGHT

    pdf.showPage()


def render_toc_pdf(
    entries: tuple[TocEntry, ...] | list[TocEntry],
    output_path: Path | None = None,
    measure_only: bool = False,
) -> int:
    entry_list = list(entries)
    page_count = max(1, (len(entry_list) + LINES_PER_PAGE - 1) // LINES_PER_PAGE)

    if measure_only:
        return page_count

    buffer = BytesIO()
    page_width, page_height = letter
    pdf = canvas.Canvas(buffer, pagesize=letter)

    if not entry_list:
        pdf.setFont(TITLE_FONT, 18)
        pdf.drawString(LEFT_MARGIN, page_height - TOP_MARGIN, "Contents")
        pdf.showPage()
    else:
        for page_index in range(page_count):
            _draw_toc_page(pdf, entry_list, page_index, page_width, page_height)

    pdf.save()
    data = buffer.getvalue()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)

    return len(PdfReader(BytesIO(data)).pages)
