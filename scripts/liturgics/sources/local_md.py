from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from liturgics.md.pdf import markdown_to_pdf
from liturgics.md.render import render_markdown
from liturgics.models import Component, Config, ResolvedComponent
from liturgics.sources.base import cache_key


def resolve_local_md(component: Component, config: Config) -> ResolvedComponent:
    source_path = config.project_root / component.path
    if not source_path.is_file():
        raise FileNotFoundError(f"Markdown file not found: {source_path}")

    rendered = render_markdown(source_path, config.project_root, component.config)
    pdf_bytes = markdown_to_pdf(rendered)

    config_suffix = str(sorted((component.config or {}).items()))
    cache_path = config.cache_dir / "md" / f"{cache_key(component.key, component.path, config_suffix)}.pdf"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(pdf_bytes)

    page_count = len(PdfReader(str(cache_path)).pages)
    if page_count == 0:
        raise ValueError(f"Rendered markdown produced no pages: {source_path}")

    return ResolvedComponent(
        component=component,
        pdf_path=cache_path,
        page_count=page_count,
    )
