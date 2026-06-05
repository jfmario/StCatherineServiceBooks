from __future__ import annotations

from liturgics.models import (
    LayoutPlan,
    LayoutSlot,
    PageKind,
    ResolvedComponent,
    Side,
    TocEntry,
)
from liturgics.sources.base import page_side
from liturgics.toc import render_toc_pdf


LINES_PER_TOC_PAGE = 40


def estimate_toc_pages(entry_count: int) -> int:
    lines = max(entry_count, 1) + 2
    return max(1, (lines + LINES_PER_TOC_PAGE - 1) // LINES_PER_TOC_PAGE)


def first_recto_after(physical_page: int) -> int:
    page = physical_page + 1
    while page_side(page) != "recto":
        page += 1
    return page


def printed_page_for_physical(physical: int, first_numbered: int) -> int | None:
    if physical < first_numbered:
        return None
    return physical - first_numbered + 1


def toc_printed_page(start_physical: int, first_numbered: int) -> int:
    if start_physical >= first_numbered:
        return start_physical - first_numbered + 1
    return 1


def _append_blank(
    slots: list[LayoutSlot],
    page_number_map: dict[int, int],
    physical: int,
    first_numbered: int,
    *,
    printed_override: int | None = None,
) -> int:
    printed = printed_override
    if printed is None:
        printed = printed_page_for_physical(physical, first_numbered)

    slots.append(LayoutSlot(kind=PageKind.BLANK, printed_page=printed))
    if printed is not None:
        page_number_map[len(slots)] = printed
    return physical + 1


def _prepare_first_component(
    slots: list[LayoutSlot],
    page_number_map: dict[int, int],
    physical: int,
    first_numbered: int,
    component: ResolvedComponent,
) -> int:
    """Align the first component; printed page 1 is always recto."""
    side = component.component.side

    if side is not None:
        while page_side(physical) != side.value:
            physical = _append_blank(
                slots,
                page_number_map,
                physical,
                first_numbered,
            )

    while physical < first_numbered:
        physical = _append_blank(
            slots, page_number_map, physical, first_numbered
        )

    if side == Side.VERSO:
        if physical == first_numbered:
            physical = _append_blank(
                slots,
                page_number_map,
                physical,
                first_numbered,
                printed_override=1,
            )

    return physical


def _build_slots(
    resolved: list[ResolvedComponent],
    toc_page_count: int,
    instructions_page_count: int = 0,
) -> tuple[list[LayoutSlot], list[TocEntry], dict[int, int]]:
    slots: list[LayoutSlot] = []
    toc_entries: list[TocEntry] = []

    slots.append(LayoutSlot(kind=PageKind.COVER))
    slots.append(LayoutSlot(kind=PageKind.BLANK))  # blank verso (back of cover leaf)

    for _ in range(instructions_page_count):
        slots.append(LayoutSlot(kind=PageKind.INSTRUCTIONS))

    for _ in range(toc_page_count):
        slots.append(LayoutSlot(kind=PageKind.TOC))

    toc_end = 2 + instructions_page_count + toc_page_count
    first_numbered = first_recto_after(toc_end)
    physical = toc_end + 1

    page_number_map: dict[int, int] = {}

    for component_index, item in enumerate(resolved):
        component = item.component

        if component_index == 0:
            physical = _prepare_first_component(
                slots, page_number_map, physical, first_numbered, item
            )
        elif component.side is not None:
            while page_side(physical) != component.side.value:
                physical = _append_blank(
                    slots, page_number_map, physical, first_numbered
                )

        if not component.toc_exempt:
            toc_entries.append(
                TocEntry(
                    name=component.name,
                    printed_page=toc_printed_page(physical, first_numbered),
                )
            )

        for _page_offset in range(item.page_count):
            printed = printed_page_for_physical(physical, first_numbered)
            slots.append(
                LayoutSlot(
                    kind=PageKind.COMPONENT,
                    component_index=component_index,
                    printed_page=printed,
                )
            )
            if printed is not None:
                page_number_map[len(slots)] = printed
            physical += 1

    while len(slots) % 2 != 0:
        slots.append(LayoutSlot(kind=PageKind.BLANK))
        physical += 1

    return slots, toc_entries, page_number_map


def plan_layout(
    resolved: list[ResolvedComponent],
    instructions_page_count: int = 0,
) -> LayoutPlan:
    toc_entry_count = sum(1 for item in resolved if not item.component.toc_exempt)
    toc_pages = estimate_toc_pages(toc_entry_count)

    for _ in range(5):
        slots, toc_entries, page_number_map = _build_slots(
            resolved, toc_pages, instructions_page_count
        )
        actual_toc_pages = render_toc_pdf(toc_entries, measure_only=True)
        if actual_toc_pages == toc_pages:
            return LayoutPlan(
                slots=tuple(slots),
                toc_entries=tuple(toc_entries),
                page_number_map=page_number_map,
            )
        toc_pages = actual_toc_pages

    slots, toc_entries, page_number_map = _build_slots(
        resolved, toc_pages, instructions_page_count
    )
    return LayoutPlan(
        slots=tuple(slots),
        toc_entries=tuple(toc_entries),
        page_number_map=page_number_map,
    )
