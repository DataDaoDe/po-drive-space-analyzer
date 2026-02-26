#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

NUM_PREFIX_RE = re.compile(r"^\d{4}_.+")


def iter_numbered_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    dirs = [p for p in root.iterdir() if p.is_dir() and NUM_PREFIX_RE.match(p.name)]
    # Sort lexicographically => 0001_..., 0002_..., ...
    return sorted(dirs, key=lambda p: p.name)


def generate_set_file(
    *,
    root: Path,
    kind: str,            # "features" or "specs"
    leaf_filename: str,   # "feature.tex" or "spec.tex"
    out_path: Path,
) -> None:
    numbered = iter_numbered_dirs(root)

    lines: list[str] = []
    lines.append("% AUTO-GENERATED. DO NOT EDIT.\n")

    missing: list[str] = []
    for d in numbered:
        leaf = d / leaf_filename
        if not leaf.exists():
            missing.append(str(leaf))
            continue

        # (correct since lualatex runs in docs/)
        # out_path is root/__all__/... so "../<root>/<dir>/<leaf>" is correct
        rel = Path("..") / root.name / d.name / leaf_filename
        lines.append(f"\\input{{{rel.as_posix()}}}\n")
        lines.append("\\clearpage\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(lines), encoding="utf-8")

    if missing:
        msg = "\n".join(missing)
        raise SystemExit(
            f"[ERROR] Some {kind} folders are missing {leaf_filename}:\n{msg}\n"
        )


def cmd_features(args: argparse.Namespace) -> None:
    root = Path(args.repo_root) / "features"
    out = root / "__all__" / "feature_set.tex"
    generate_set_file(
        root=root,
        kind="features",
        leaf_filename="feature.tex",
        out_path=out,
    )
    print(f"Wrote: {out}")


def cmd_specs(args: argparse.Namespace) -> None:
    root = Path(args.repo_root) / "specs"
    out = root / "__all__" / "spec_set.tex"
    generate_set_file(
        root=root,
        kind="specs",
        leaf_filename="spec.tex",
        out_path=out,
    )
    print(f"Wrote: {out}")


def cmd_all(args: argparse.Namespace) -> None:
    # Generate both
    cmd_features(args)
    cmd_specs(args)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate feature/spec rollup TeX files under __all__/"
    )
    p.add_argument(
        "--repo-root",
        default=".",
        help="Path to repo root (default: .)",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sp_features = sub.add_parser("features", help="Generate features/__all__/feature_set.tex")
    sp_features.set_defaults(func=cmd_features)

    sp_specs = sub.add_parser("specs", help="Generate specs/__all__/spec_set.tex")
    sp_specs.set_defaults(func=cmd_specs)

    sp_all = sub.add_parser("all", help="Generate both sets")
    sp_all.set_defaults(func=cmd_all)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()