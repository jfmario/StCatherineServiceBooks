from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def find_project_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path(__file__).resolve()

    for candidate in [start, *start.parents]:
        if (candidate / "projects").is_dir() and (candidate / "scripts").is_dir():
            return candidate

    return Path(__file__).resolve().parents[2]


def load_env(project_root: Path) -> None:
    load_dotenv(project_root / ".env")
