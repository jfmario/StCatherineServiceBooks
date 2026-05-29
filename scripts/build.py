#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from liturgics.config import find_project_root
from liturgics.loader import YamlValidationError
from liturgics.pipeline import build_project


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Liturgics PDF from a project YAML file.")
    parser.add_argument("yaml_path", type=Path, help="Path to the project YAML file")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repository root (defaults to auto-detect)",
    )
    args = parser.parse_args()

    yaml_path = args.yaml_path.resolve()
    project_root = args.project_root.resolve() if args.project_root else None

    try:
        output_path = build_project(yaml_path, project_root=project_root or find_project_root(yaml_path.parent))
    except (YamlValidationError, ValueError, FileNotFoundError, EnvironmentError, NotImplementedError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
