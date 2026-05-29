from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from liturgics.fonts import BODY_FONT
from liturgics.sources.base import page_side


FOOTER_MARGIN = 0.75 * inch
FONT_SIZE = 10


def _blank_page_pdf() -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def _page_number_overlay(printed_page: int, physical_page: int) -> bytes:
    buffer = BytesIO()
    page_width, page_height = letter
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont(BODY_FONT, FONT_SIZE)
    label = str(printed_page)
    text_width = pdf.stringWidth(label, BODY_FONT, FONT_SIZE)
    y = FOOTER_MARGIN

    if page_side(physical_page) == "recto":
        x = page_width - FOOTER_MARGIN - text_width
    else:
        x = FOOTER_MARGIN

    pdf.drawString(x, y, label)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def _merge_overlay(base_page, overlay_pdf: bytes):
    overlay_reader = PdfReader(BytesIO(overlay_pdf))
    base_page.merge_page(overlay_reader.pages[0])
    return base_page


def add_page_numbers(input_pdf: bytes, page_number_map: dict[int, int]) -> bytes:
    reader = PdfReader(BytesIO(input_pdf))
    writer = PdfWriter()
    blank_page = _blank_page_pdf()

    for index, page in enumerate(reader.pages, start=1):
        if index in page_number_map:
            overlay = _page_number_overlay(page_number_map[index], index)
            page = _merge_overlay(page, overlay)
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def blank_page_bytes() -> bytes:
    return _blank_page_pdf()
