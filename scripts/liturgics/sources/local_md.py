from __future__ import annotations

from liturgics.models import Component, Config, ResolvedComponent


def resolve_local_md(component: Component, config: Config) -> ResolvedComponent:
    raise NotImplementedError("local-md will be rendered with Jinja")
