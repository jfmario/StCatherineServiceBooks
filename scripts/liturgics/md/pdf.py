from __future__ import annotations

import re
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from liturgics.fonts import BODY_FONT, TITLE_FONT


MARGIN = 1 * inch
HEADING_SPACE_BEFORE = 12
HEADING_SPACE_AFTER = 6
BODY_SPACE_AFTER = 8
HEADING_SIZE = 16
BODY_SIZE = 14
LEADING = 18

_ITALIC_PATTERN = re.compile(r"\*(.+?)\*")


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _inline_markup(text: str) -> str:
    escaped = _escape_xml(text)

    def replace_italic(match: re.Match[str]) -> str:
        return f"<i>{match.group(1)}</i>"

    return _ITALIC_PATTERN.sub(replace_italic, escaped)


def _parse_blocks(markdown: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for block in re.split(r"\n\s*\n", markdown.strip()):
        content = block.strip()
        if not content:
            continue
        if content.startswith("## "):
            blocks.append(("heading", content[3:].strip()))
        else:
            blocks.append(("body", content))
    return blocks


def markdown_to_pdf(markdown: str) -> bytes:
    heading_style = ParagraphStyle(
        name="Heading",
        fontName=TITLE_FONT,
        fontSize=HEADING_SIZE,
        leading=HEADING_SIZE + 2,
        spaceBefore=HEADING_SPACE_BEFORE,
        spaceAfter=HEADING_SPACE_AFTER,
    )
    body_style = ParagraphStyle(
        name="Body",
        fontName=BODY_FONT,
        fontSize=BODY_SIZE,
        leading=LEADING,
        spaceAfter=BODY_SPACE_AFTER,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    story: list = []
    for kind, text in _parse_blocks(markdown):
        if kind == "heading":
            story.append(Paragraph(_inline_markup(text), heading_style))
        else:
            for line in text.splitlines():
                line = line.strip()
                if line:
                    story.append(Paragraph(_inline_markup(line), body_style))
            story.append(Spacer(1, BODY_SPACE_AFTER / 2))

    if not story:
        story.append(Spacer(1, 1))

    doc.build(story)
    return buffer.getvalue()
