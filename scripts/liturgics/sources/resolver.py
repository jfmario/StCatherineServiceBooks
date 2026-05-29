from __future__ import annotations

from liturgics.models import ComponentType, Config, Project, ResolvedComponent
from liturgics.sources.library_pdf import resolve_library_pdf
from liturgics.sources.local_md import resolve_local_md
from liturgics.sources.local_pdf import resolve_local_pdf


def resolve_components(project: Project, config: Config) -> list[ResolvedComponent]:
    resolved: list[ResolvedComponent] = []
    for component in project.components:
        if component.type == ComponentType.LOCAL_PDF:
            resolved.append(resolve_local_pdf(component, config))
        elif component.type == ComponentType.LIBRARY_PDF:
            resolved.append(resolve_library_pdf(component, config))
        elif component.type == ComponentType.LOCAL_MD:
            resolved.append(resolve_local_md(component, config))
        else:
            raise ValueError(f"Unsupported component type: {component.type}")
    return resolved
