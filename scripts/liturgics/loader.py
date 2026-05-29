from __future__ import annotations

from pathlib import Path

import yaml

from liturgics.models import (
    Component,
    ComponentType,
    PageRange,
    Project,
    Side,
)


class YamlValidationError(ValueError):
    pass


def _require_str(data: dict, key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise YamlValidationError(f"{context}: '{key}' must be a non-empty string")
    return value.strip()


def _optional_str(data: dict, key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise YamlValidationError(f"'{key}' must be a string when provided")
    return value.strip() or None


def _parse_page_range(raw: object, context: str) -> PageRange | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise YamlValidationError(f"{context}: 'Pages' must be a mapping")

    start = raw.get("Start")
    end = raw.get("End")
    if start is not None and not isinstance(start, int):
        raise YamlValidationError(f"{context}: 'Pages.Start' must be an integer")
    if end is not None and not isinstance(end, int):
        raise YamlValidationError(f"{context}: 'Pages.End' must be an integer")
    if start is not None and start < 1:
        raise YamlValidationError(f"{context}: 'Pages.Start' must be >= 1")
    if end is not None and end < 1:
        raise YamlValidationError(f"{context}: 'Pages.End' must be >= 1")
    if start is not None and end is not None and end < start:
        raise YamlValidationError(f"{context}: 'Pages.End' must be >= 'Pages.Start'")

    return PageRange(start=start, end=end)


def _parse_component(raw: object, index: int) -> Component:
    context = f"Components[{index}]"
    if not isinstance(raw, dict):
        raise YamlValidationError(f"{context} must be a mapping")

    key = _require_str(raw, "Key", context)
    name = _require_str(raw, "Name", context)
    type_raw = _require_str(raw, "Type", context)

    try:
        component_type = ComponentType(type_raw)
    except ValueError as exc:
        allowed = ", ".join(t.value for t in ComponentType)
        raise YamlValidationError(
            f"{context}: 'Type' must be one of: {allowed}"
        ) from exc

    path = _require_str(raw, "Path", context)

    toc_exempt = raw.get("TocExempt", False)
    if not isinstance(toc_exempt, bool):
        raise YamlValidationError(f"{context}: 'TocExempt' must be a boolean")

    pages = _parse_page_range(raw.get("Pages"), context)

    side_raw = raw.get("Side")
    side: Side | None = None
    if side_raw is not None:
        if not isinstance(side_raw, str):
            raise YamlValidationError(f"{context}: 'Side' must be a string")
        try:
            side = Side(side_raw)
        except ValueError as exc:
            allowed = ", ".join(s.value for s in Side)
            raise YamlValidationError(
                f"{context}: 'Side' must be one of: {allowed}"
            ) from exc

    return Component(
        key=key,
        name=name,
        type=component_type,
        path=path,
        toc_exempt=toc_exempt,
        pages=pages,
        side=side,
    )


def load_project(yaml_path: Path) -> Project:
    if not yaml_path.is_file():
        raise FileNotFoundError(f"Project YAML not found: {yaml_path}")

    with yaml_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise YamlValidationError("Project YAML root must be a mapping")

    name = _require_str(data, "Name", "Project")
    filename = _require_str(data, "Filename", "Project")
    subtitle = _optional_str(data, "Subtitle")
    description = _optional_str(data, "Description")

    raw_components = data.get("Components")
    if not isinstance(raw_components, list) or not raw_components:
        raise YamlValidationError("'Components' must be a non-empty list")

    components = tuple(_parse_component(item, i) for i, item in enumerate(raw_components))
    keys = [component.key for component in components]
    if len(keys) != len(set(keys)):
        raise YamlValidationError("Component 'Key' values must be unique")

    return Project(
        name=name,
        filename=filename,
        subtitle=subtitle,
        description=description,
        components=components,
    )
