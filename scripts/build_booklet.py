#!/usr/bin/env python3
"""Build a congregational booklet PDF from a LaTeX project file."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from liturgics.config import find_project_root

# MacTeX installs here and doesn't always make it onto PATH in non-login shells.
_MACTEX_BIN = Path("/Library/TeX/texbin")


def _find_pdflatex() -> str:
    if shutil.which("pdflatex"):
        return "pdflatex"
    candidate = _MACTEX_BIN / "pdflatex"
    if candidate.exists():
        return str(candidate)
    raise FileNotFoundError(
        "pdflatex not found. Install MacTeX (brew install --cask mactex-no-gui) "
        "or ensure pdflatex is on your PATH."
    )


def build_booklet(tex_path: Path, project_root: Path | None = None) -> Path:
    tex_path = tex_path.resolve()
    root = project_root or find_project_root(tex_path.parent)
    out_dir = root / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Run pdflatex twice from the project root so \input{} paths resolve
        # correctly and page references stabilise.
        cmd = [
            _find_pdflatex(),
            "-interaction=nonstopmode",
            f"-output-directory={tmp_path}",
            str(tex_path),
        ]
        for _ in range(2):
            result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
            if result.returncode != 0:
                # Print the tail of the log for useful error context
                log_file = tmp_path / tex_path.with_suffix(".log").name
                if log_file.exists():
                    lines = log_file.read_text(errors="replace").splitlines()
                    print("\n".join(lines[-40:]), file=sys.stderr)
                else:
                    print(result.stdout[-3000:], file=sys.stderr)
                raise RuntimeError(f"pdflatex failed (exit {result.returncode})")

        pdf_name = tex_path.with_suffix(".pdf").name
        output_path = out_dir / pdf_name
        shutil.copy(tmp_path / pdf_name, output_path)

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a congregational booklet PDF from a LaTeX project file."
    )
    parser.add_argument("tex_path", type=Path, help="Path to the project .tex file")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repository root (defaults to auto-detect)",
    )
    args = parser.parse_args()

    tex_path = args.tex_path.resolve()
    project_root = args.project_root.resolve() if args.project_root else None

    try:
        output_path = build_booklet(
            tex_path,
            project_root=project_root or find_project_root(tex_path.parent),
        )
    except (RuntimeError, FileNotFoundError, EnvironmentError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
