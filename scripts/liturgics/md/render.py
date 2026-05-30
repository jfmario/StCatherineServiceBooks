from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def _load_data_file(data_dir: Path, name: str) -> dict[str, Any]:
    path = data_dir / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {path}")

    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Data file must be a mapping: {path}")

    return data


def render_markdown(source_path: Path, project_root: Path) -> str:
    post = frontmatter.load(source_path)
    metadata = dict(post.metadata)
    data_dir_name = metadata.get("data", "data")
    data_dir = project_root / data_dir_name
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    cache: dict[str, dict[str, Any]] = {}

    def ref(name: str, key: str) -> Any:
        if name not in cache:
            cache[name] = _load_data_file(data_dir, name)
        data = cache[name]
        if key not in data:
            raise KeyError(f"Key '{key}' not found in {data_dir / f'{name}.yaml'}")
        return data[key]

    components_dir = project_root / "components"
    env = Environment(
        loader=FileSystemLoader(str(components_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    template = env.from_string(post.content)
    return template.render(ref=ref, metadata=metadata, **metadata)
