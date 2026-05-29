from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ComponentType(str, Enum):
    LIBRARY_PDF = "library-pdf"
    LOCAL_PDF = "local-pdf"
    LOCAL_MD = "local-md"


class Side(str, Enum):
    VERSO = "verso"
    RECTO = "recto"


@dataclass(frozen=True)
class PageRange:
    start: int | None = None
    end: int | None = None


@dataclass(frozen=True)
class Component:
    key: str
    name: str
    type: ComponentType
    path: str
    toc_exempt: bool = False
    pages: PageRange | None = None
    side: Side | None = None


@dataclass(frozen=True)
class Project:
    name: str
    filename: str
    subtitle: str | None = None
    description: str | None = None
    components: tuple[Component, ...] = ()


@dataclass(frozen=True)
class ResolvedComponent:
    component: Component
    pdf_path: Path
    page_count: int


@dataclass(frozen=True)
class TocEntry:
    name: str
    printed_page: int


class PageKind(str, Enum):
    COVER = "cover"
    TOC = "toc"
    BLANK = "blank"
    COMPONENT = "component"


@dataclass(frozen=True)
class LayoutSlot:
    kind: PageKind
    component_index: int | None = None
    printed_page: int | None = None


@dataclass(frozen=True)
class LayoutPlan:
    slots: tuple[LayoutSlot, ...]
    toc_entries: tuple[TocEntry, ...]
    page_number_map: dict[int, int]


@dataclass
class Config:
    project_root: Path
    library_bucket: str | None
    aws_region: str | None
    cache_dir: Path
    out_dir: Path

    @classmethod
    def from_env(cls, project_root: Path) -> Config:
        return cls(
            project_root=project_root,
            library_bucket=os.environ.get("LITURGICS_LIBRARY_BUCKET") or None,
            aws_region=os.environ.get("AWS_REGION") or None,
            cache_dir=project_root / ".cache",
            out_dir=project_root / "out",
        )
