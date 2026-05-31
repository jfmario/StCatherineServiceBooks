from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

_RESERVED_KEYS = frozenset({"template", "config", "data", "as"})


def _load_data_file(data_dir: Path, name: str) -> dict[str, Any]:
    path = data_dir / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {path}")

    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Data file must be a mapping: {path}")

    return data


def _merge_config(
    front_matter: dict[str, Any],
    component_config: dict[str, Any] | None,
) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    raw = front_matter.get("config")
    if isinstance(raw, dict):
        merged.update(raw)
    if component_config:
        merged.update(component_config)
    return merged


def _content_object(metadata: dict[str, Any], body: str) -> dict[str, Any]:
    obj = {
        key: value
        for key, value in metadata.items()
        if key not in _RESERVED_KEYS
    }
    obj["content"] = body.strip()
    return obj


def render_markdown(
    source_path: Path,
    project_root: Path,
    component_config: dict[str, Any] | None = None,
) -> str:
    post = frontmatter.load(source_path)
    metadata = dict(post.metadata)
    components_dir = project_root / "components"

    data_dir: Path | None = None
    data_dir_name = metadata.get("data")
    if data_dir_name is not None:
        data_dir = project_root / data_dir_name
        if not data_dir.is_dir():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

    cache: dict[str, dict[str, Any]] = {}

    def ref(name: str, key: str) -> Any:
        if data_dir is None:
            data_dir_path = project_root / "data"
            if not data_dir_path.is_dir():
                raise FileNotFoundError(
                    "Data directory not found. Set 'data' in front matter or create data/."
                )
            resolved_data_dir = data_dir_path
        else:
            resolved_data_dir = data_dir

        if name not in cache:
            cache[name] = _load_data_file(resolved_data_dir, name)
        data = cache[name]
        if key not in data:
            raise KeyError(f"Key '{key}' not found in {resolved_data_dir / f'{name}.yaml'}")
        return data[key]

    env = Environment(
        loader=FileSystemLoader(str(components_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    render_config = _merge_config(metadata, component_config)
    context: dict[str, Any] = {
        "ref": ref,
        "metadata": metadata,
        "config": render_config,
    }

    template_name = metadata.get("template")
    if template_name:
        var_name = metadata.get("as") or Path(template_name).stem
        context[var_name] = _content_object(metadata, post.content)
        template = env.get_template(template_name)
    else:
        for key, value in metadata.items():
            if key not in _RESERVED_KEYS:
                context[key] = value
        template = env.from_string(post.content)

    return template.render(**context)
