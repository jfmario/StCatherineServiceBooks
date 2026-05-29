from __future__ import annotations

from pathlib import Path

from liturgics.models import Component, Config, ResolvedComponent
from liturgics.sources.base import cache_key, slice_pdf


def resolve_local_pdf(component: Component, config: Config) -> ResolvedComponent:
    source_path = config.project_root / component.path
    if not source_path.is_file():
        raise FileNotFoundError(f"Local PDF not found: {source_path}")

    cache_path = config.cache_dir / "local" / f"{cache_key(component.key, component.path)}.pdf"
    page_count = slice_pdf(source_path, component.pages, cache_path)

    return ResolvedComponent(
        component=component,
        pdf_path=cache_path,
        page_count=page_count,
    )
