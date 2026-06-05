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
TITLE_SIZE = 20
LEADING = 18
LIST_INDENT = 18
BULLET_INDENT = 8

_BOLD_PATTERN = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_PATTERN = re.compile(r"(?<![*\[])\*([^*]+)\*(?![*\]])")
_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_ORDERED_ITEM_PATTERN = re.compile(r"^\d+\.\s+(.*)$")
_LITERAL_NUMBERED_PATTERN = re.compile(r"^\d+\)\s")
_BULLET_PREFIXES = ("- ", "* ", "+ ")


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _inline_markup(text: str) -> str:
    parts: list[str] = []
    last = 0
    for match in _LINK_PATTERN.finditer(text):
        parts.append(_escape_xml(text[last : match.start()]))
        label = _escape_xml(match.group(1))
        url = _escape_xml(match.group(2))
        parts.append(f'<a href="{url}" color="blue">{label}</a>')
        last = match.end()
    parts.append(_escape_xml(text[last:]))
    combined = "".join(parts)

    def replace_bold(match: re.Match[str]) -> str:
        return f"<b>{match.group(1)}</b>"

    def replace_italic(match: re.Match[str]) -> str:
        return f"<i>{match.group(1)}</i>"

    combined = _BOLD_PATTERN.sub(replace_bold, combined)
    return _ITALIC_PATTERN.sub(replace_italic, combined)


def _is_bullet_line(line: str) -> bool:
    return any(line.startswith(prefix) for prefix in _BULLET_PREFIXES)


def _bullet_text(line: str) -> str:
    for prefix in _BULLET_PREFIXES:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return line.strip()


def _parse_blocks(markdown: str) -> list[tuple[str, str | list[str]]]:
    blocks: list[tuple[str, str | list[str]]] = []
    lines = markdown.strip().splitlines()
    index = 0

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("# "):
            blocks.append(("title", stripped[2:].strip()))
            index += 1
            continue

        if stripped.startswith("## "):
            blocks.append(("heading", stripped[3:].strip()))
            index += 1
            continue

        if _is_bullet_line(stripped):
            items: list[str] = []
            while index < len(lines):
                current = lines[index].strip()
                if not current:
                    index += 1
                    break
                if _is_bullet_line(current):
                    items.append(_bullet_text(current))
                    index += 1
                    continue
                break
            blocks.append(("bullet_list", items))
            continue

        if _LITERAL_NUMBERED_PATTERN.match(stripped):
            blocks.append(("paragraph", stripped))
            index += 1
            continue

        ordered_match = _ORDERED_ITEM_PATTERN.match(stripped)
        if ordered_match:
            items = [ordered_match.group(1)]
            index += 1
            while index < len(lines):
                current = lines[index].strip()
                if not current:
                    index += 1
                    break
                next_match = _ORDERED_ITEM_PATTERN.match(current)
                if next_match:
                    items.append(next_match.group(1))
                    index += 1
                    continue
                break
            blocks.append(("ordered_list", items))
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            current = lines[index].strip()
            if not current:
                index += 1
                break
            if (
                current.startswith("#")
                or _is_bullet_line(current)
                or _ORDERED_ITEM_PATTERN.match(current)
                or _LITERAL_NUMBERED_PATTERN.match(current)
            ):
                break
            paragraph_lines.append(current)
            index += 1
        blocks.append(("paragraph", " ".join(paragraph_lines)))

    return blocks


def markdown_to_pdf(markdown: str) -> bytes:
    title_style = ParagraphStyle(
        name="Title",
        fontName=TITLE_FONT,
        fontSize=TITLE_SIZE,
        leading=TITLE_SIZE + 4,
        spaceBefore=0,
        spaceAfter=HEADING_SPACE_AFTER,
    )
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
    bullet_style = ParagraphStyle(
        name="Bullet",
        parent=body_style,
        leftIndent=LIST_INDENT,
        bulletIndent=BULLET_INDENT,
        spaceAfter=BODY_SPACE_AFTER / 2,
    )
    ordered_style = ParagraphStyle(
        name="Ordered",
        parent=body_style,
        leftIndent=LIST_INDENT,
        bulletIndent=BULLET_INDENT,
        spaceAfter=BODY_SPACE_AFTER / 2,
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
    for kind, content in _parse_blocks(markdown):
        if kind == "title":
            story.append(Paragraph(_inline_markup(str(content)), title_style))
        elif kind == "heading":
            story.append(Paragraph(_inline_markup(str(content)), heading_style))
        elif kind == "paragraph":
            story.append(Paragraph(_inline_markup(str(content)), body_style))
        elif kind == "bullet_list":
            for item in content:
                story.append(
                    Paragraph(
                        f'<bullet>&bull;</bullet>{_inline_markup(item)}',
                        bullet_style,
                    )
                )
            story.append(Spacer(1, BODY_SPACE_AFTER / 2))
        elif kind == "ordered_list":
            for number, item in enumerate(content, start=1):
                story.append(
                    Paragraph(
                        f'<bullet>{number}.</bullet>{_inline_markup(item)}',
                        ordered_style,
                    )
                )
            story.append(Spacer(1, BODY_SPACE_AFTER / 2))

    if not story:
        story.append(Spacer(1, 1))

    doc.build(story)
    return buffer.getvalue()
