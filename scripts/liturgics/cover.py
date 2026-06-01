from __future__ import annotations

from datetime import date
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from liturgics.fonts import BODY_FONT, TITLE_FONT


def _revision_label(when: date | None = None) -> str:
    today = when or date.today()
    return f"Revision: {today.strftime('%b')} {today.day}, {today.year}"


def build_cover_pdf(
    name: str,
    subtitle: str | None,
    revision_date: date | None = None,
) -> bytes:
    buffer = BytesIO()
    page_width, page_height = letter
    pdf = canvas.Canvas(buffer, pagesize=letter)

    center_y = page_height / 2

    pdf.setFont(TITLE_FONT, 24)
    title_width = pdf.stringWidth(name, TITLE_FONT, 24)
    pdf.drawString((page_width - title_width) / 2, center_y + 24, name)

    y = center_y - 8
    if subtitle:
        pdf.setFont(BODY_FONT, 16)
        subtitle_width = pdf.stringWidth(subtitle, BODY_FONT, 16)
        pdf.drawString((page_width - subtitle_width) / 2, y, subtitle)
        y -= 28

    pdf.setFont(BODY_FONT, 12)
    revision = _revision_label(revision_date)
    revision_width = pdf.stringWidth(revision, BODY_FONT, 12)
    pdf.drawString((page_width - revision_width) / 2, y, revision)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
