from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from liturgics.cover import build_cover_pdf
from liturgics.models import Config, LayoutPlan, PageKind, Project, ResolvedComponent, ResolvedInstructions
from liturgics.page_numbers import add_page_numbers, blank_page_bytes
from liturgics.toc import render_toc_pdf


def _append_pdf_bytes(writer: PdfWriter, data: bytes) -> None:
    reader = PdfReader(BytesIO(data))
    for page in reader.pages:
        writer.add_page(page)


def _append_pdf_page(writer: PdfWriter, reader: PdfReader, page_index: int) -> None:
    writer.add_page(reader.pages[page_index])


def assemble_pdf(
    project: Project,
    resolved: list[ResolvedComponent],
    plan: LayoutPlan,
    config: Config,
    instructions: ResolvedInstructions | None = None,
) -> bytes:
    writer = PdfWriter()
    blank = blank_page_bytes()
    cover = build_cover_pdf(project.name, project.subtitle)

    instructions_reader = (
        PdfReader(str(instructions.pdf_path)) if instructions is not None else None
    )
    instructions_page_index = 0

    toc_path = config.cache_dir / "toc-temp.pdf"
    render_toc_pdf(plan.toc_entries, output_path=toc_path)
    toc_reader = PdfReader(str(toc_path))

    component_readers = [PdfReader(str(item.pdf_path)) for item in resolved]
    component_page_indices = [0] * len(resolved)
    toc_page_index = 0

    for slot_index, slot in enumerate(plan.slots, start=1):
        if slot.kind == PageKind.COVER:
            _append_pdf_bytes(writer, cover)
        elif slot.kind == PageKind.INSTRUCTIONS:
            if instructions_reader is None:
                raise ValueError(f"Instructions slot at position {slot_index} but no instructions PDF")
            if instructions_page_index >= len(instructions_reader.pages):
                raise ValueError("Instructions PDF has fewer pages than planned")
            _append_pdf_page(writer, instructions_reader, instructions_page_index)
            instructions_page_index += 1
        elif slot.kind == PageKind.TOC:
            if toc_page_index >= len(toc_reader.pages):
                raise ValueError("TOC PDF has fewer pages than planned")
            _append_pdf_page(writer, toc_reader, toc_page_index)
            toc_page_index += 1
        elif slot.kind == PageKind.BLANK:
            _append_pdf_bytes(writer, blank)
        elif slot.kind == PageKind.COMPONENT:
            if slot.component_index is None:
                raise ValueError(f"Component slot missing index at position {slot_index}")
            reader = component_readers[slot.component_index]
            page_index = component_page_indices[slot.component_index]
            if page_index >= len(reader.pages):
                raise ValueError(
                    f"Component {slot.component_index} ran out of pages at slot {slot_index}"
                )
            writer.add_page(reader.pages[page_index])
            component_page_indices[slot.component_index] += 1
        else:
            raise ValueError(f"Unknown slot kind: {slot.kind}")

    buffer = BytesIO()
    writer.write(buffer)
    unnumbered = buffer.getvalue()

    page_number_map: dict[int, int] = {}
    for slot_index, slot in enumerate(plan.slots, start=1):
        if slot.printed_page is not None:
            page_number_map[slot_index] = slot.printed_page

    return add_page_numbers(unnumbered, page_number_map)
