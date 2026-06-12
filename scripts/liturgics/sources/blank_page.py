from __future__ import annotations

from liturgics.models import Component, Config, ResolvedComponent
from liturgics.page_numbers import blank_page_bytes


def resolve_blank_page(component: Component, config: Config) -> ResolvedComponent:
    cache_path = config.cache_dir / "blank" / "page.pdf"
    if not cache_path.is_file():
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(blank_page_bytes())

    return ResolvedComponent(
        component=component,
        pdf_path=cache_path,
        page_count=1,
    )
