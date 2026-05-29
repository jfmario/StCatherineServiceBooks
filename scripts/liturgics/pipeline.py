from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from liturgics.assembler import assemble_pdf
from liturgics.config import find_project_root, load_env
from liturgics.layout import plan_layout
from liturgics.loader import load_project
from liturgics.models import Config
from liturgics.sources.resolver import resolve_components


def build_project(yaml_path: Path, project_root: Path | None = None) -> Path:
    root = project_root or find_project_root(yaml_path.parent)
    load_env(root)
    config = Config.from_env(root)
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    config.out_dir.mkdir(parents=True, exist_ok=True)

    project = load_project(yaml_path)
    resolved = resolve_components(project, config)
    layout = plan_layout(resolved)
    pdf_bytes = assemble_pdf(project, resolved, layout, config)

    output_path = config.out_dir / project.filename
    output_path.write_bytes(pdf_bytes)
    return output_path
