from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from liturgics.md.pdf import markdown_to_pdf
from liturgics.md.render import render_markdown
from liturgics.models import Config, Project, ResolvedInstructions
from liturgics.sources.base import cache_key


def resolve_instructions(project: Project, config: Config) -> ResolvedInstructions | None:
    if not project.instructions:
        return None

    source_path = config.project_root / project.instructions
    if not source_path.is_file():
        raise FileNotFoundError(f"Instructions file not found: {source_path}")

    rendered = render_markdown(source_path, config.project_root)
    pdf_bytes = markdown_to_pdf(rendered)

    cache_path = config.cache_dir / "instructions" / f"{cache_key(project.instructions)}.pdf"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(pdf_bytes)

    page_count = len(PdfReader(str(cache_path)).pages)
    if page_count == 0:
        raise ValueError(f"Instructions produced no pages: {source_path}")

    return ResolvedInstructions(pdf_path=cache_path, page_count=page_count)
