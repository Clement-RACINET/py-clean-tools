"""Command-line interface for py-clean-tools."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from py_clean_tools.cleaner import build_clean_plan, execute_clean_plan


@dataclass(frozen=True, slots=True)
class CliArgs:
    """Typed command-line arguments."""

    root: Path
    write: bool
    check: bool


def build_parser() -> argparse.ArgumentParser:
    """Build and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="pyclean",
        description="Safely remove Python cache and build artifacts.",
    )
    _ = parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to clean. Defaults to current working directory.",
    )
    _ = parser.add_argument(
        "--write",
        action="store_true",
        help="Actually remove files. Without this flag, pyclean runs in dry-run mode.",
    )
    _ = parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with code 1 if cleanup targets are found.",
    )

    return parser


def parse_args(argv: list[str] | None = None) -> CliArgs:
    """Parse command-line arguments."""
    namespace = build_parser().parse_args(argv)

    return CliArgs(
        root=cast(Path, namespace.root),
        write=bool(cast(bool, namespace.write)),
        check=bool(cast(bool, namespace.check)),
    )


def _relative_to_root(path: Path, root: Path) -> Path:
    """Return a path relative to root when possible."""
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def main(argv: list[str] | None = None) -> int:
    """Run the pyclean command-line interface."""
    args = parse_args(argv)
    root = args.root.resolve()

    plan = build_clean_plan(root)

    if args.check:
        if plan.is_empty:
            print("No cleanup targets found.")
            return 0

        print("Cleanup targets found:")
        for target in plan.targets:
            print(f"  [FOUND] {_relative_to_root(target.path, root)}")
        return 1

    if plan.is_empty:
        print("Nothing to clean.")
        return 0

    if not args.write:
        print("DRY-RUN — nothing will be deleted.\n")
        for target in plan.targets:
            print(f"  [DRY-RUN] Would remove: {_relative_to_root(target.path, root)}")
        print(f"\n{len(plan.targets)} item(s) would be removed.")
        return 0

    print("Cleaning repository...\n")
    for target in plan.targets:
        print(f"  [REMOVED] {_relative_to_root(target.path, root)}")

    removed = execute_clean_plan(plan)
    print(f"\n{removed} item(s) removed.")
    return 0


def entrypoint(argv: list[str] | None = None) -> None:
    """Console-script wrapper."""
    raise SystemExit(main(argv))


if __name__ == "__main__":
    entrypoint()
