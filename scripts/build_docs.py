#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
DOCS_DIR = REPO_ROOT / "docs"
OUT_DIR = DOCS_DIR / "build"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(DOCS_DIR), check=True)


def build_tex(tex_filename: str, runs: int = 2) -> None:
    tex_path = DOCS_DIR / tex_filename
    if not tex_path.exists():
        raise SystemExit(f"[ERROR] Missing TeX entrypoint: {tex_path}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for _ in range(runs):
        run(
            [
                "lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={OUT_DIR.as_posix()}",
                tex_filename # since cwd is docs/, pass the filename not the path
            ]
        )

    pdf_path = OUT_DIR / tex_path.with_suffix(".pdf").name
    print(f"\nBuilt: {pdf_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build LaTeX documents in docs/.")
    parser.add_argument(
        "target",
        choices=["all", "features", "specs"],
        help="Which document to build",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=2,
        help="How many lualatex passes to run (default: 2)",
    )
    args = parser.parse_args()

    targets = {
        "all": "all.tex",
        "features": "features_all.tex",
        "specs": "specs_all.tex",
    }

    build_tex(targets[args.target], runs=args.runs)


if __name__ == "__main__":
    main()