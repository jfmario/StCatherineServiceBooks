from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from liturgics.fonts import BODY_FONT, TITLE_FONT


def build_cover_pdf(name: str, subtitle: str | None) -> bytes:
    buffer = BytesIO()
    page_width, page_height = letter
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont(TITLE_FONT, 24)
    title_width = pdf.stringWidth(name, TITLE_FONT, 24)
    pdf.drawString((page_width - title_width) / 2, page_height / 2 + 20, name)

    if subtitle:
        pdf.setFont(BODY_FONT, 16)
        subtitle_width = pdf.stringWidth(subtitle, BODY_FONT, 16)
        pdf.drawString((page_width - subtitle_width) / 2, page_height / 2 - 20, subtitle)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
