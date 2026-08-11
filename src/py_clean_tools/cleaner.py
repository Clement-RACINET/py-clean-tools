"""Cleanup planning and execution."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import shutil

from py_clean_tools.models import CleanPlan, CleanTarget

DEFAULT_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".pixi",
        ".venv",
        "venv",
        "node_modules",
        "__pypackages__",
    }
)

DEFAULT_DIR_NAMES: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".pyre",
        ".pytype",
        "htmlcov",
        "dist",
        "build",
    }
)

DEFAULT_DIR_GLOBS: tuple[str, ...] = ("*.egg-info",)

DEFAULT_FILE_GLOBS: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    "coverage.xml",
)

@dataclass(frozen=True, slots=True)
class CleanFailure:
    """A cleanup failure."""

    target: CleanTarget
    error: OSError


@dataclass(frozen=True, slots=True)
class CleanExecutionResult:
    """Result of cleanup execution."""

    removed: tuple[CleanTarget, ...]
    failures: tuple[CleanFailure, ...]

    @property
    def removed_count(self) -> int:
        """Return the number of removed targets."""
        return len(self.removed)

    @property
    def failed_count(self) -> int:
        """Return the number of failed targets."""
        return len(self.failures)

    @property
    def has_failures(self) -> bool:
        """Return whether cleanup had failures."""
        return bool(self.failures)


def is_excluded(path: Path, root: Path, excluded_dirs: Iterable[str]) -> bool:
    """Return whether a path is inside an excluded directory."""
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True

    excluded = set(excluded_dirs)
    return any(part in excluded for part in rel_parts)


def iter_dirs(root: Path, excluded_dirs: Iterable[str]) -> Iterable[Path]:
    """Iterate through directories while pruning excluded directories."""
    excluded = set(excluded_dirs)

    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        if any(part in excluded for part in path.relative_to(root).parts):
            continue
        yield path


def build_clean_plan(
    root: Path,
    *,
    dir_names: Iterable[str] = DEFAULT_DIR_NAMES,
    dir_globs: Iterable[str] = DEFAULT_DIR_GLOBS,
    file_globs: Iterable[str] = DEFAULT_FILE_GLOBS,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
) -> CleanPlan:
    """Build a deterministic cleanup plan for a repository."""
    root = root.resolve()
    targets: dict[Path, CleanTarget] = {}

    dir_name_set = set(dir_names)

    for directory in iter_dirs(root, excluded_dirs):
        if directory.name in dir_name_set:
            reason_message = f"directory name: {directory.name}"
            targets[directory] = CleanTarget(directory, reason_message)

    for pattern in dir_globs:
        for match in root.glob(pattern):
            if match.is_dir() and not is_excluded(match, root, excluded_dirs):
                targets[match] = CleanTarget(match, f"directory glob: {pattern}")

    for pattern in file_globs:
        iterator = root.rglob(pattern) if "*" in pattern else root.glob(pattern)

        for match in iterator:
            if match.is_file() and not is_excluded(match, root, excluded_dirs):
                targets[match] = CleanTarget(match, f"file glob: {pattern}")

    sorted_targets = sorted(
        targets.values(),
        key=lambda target: target.path.as_posix(),
    )

    return CleanPlan(tuple(sorted_targets))


def remove_target(target: CleanTarget) -> None:
    """Remove a single cleanup target."""
    if target.path.is_dir():
        shutil.rmtree(target.path)
    else:
        target.path.unlink()


def execute_clean_plan(plan: CleanPlan) -> CleanExecutionResult:
    """Execute a cleanup plan and return execution details."""
    removed: list[CleanTarget] = []
    failures: list[CleanFailure] = []

    for target in plan.targets:
        if not target.path.exists():
            continue

        try:
            remove_target(target)
        except OSError as exc:
            failures.append(CleanFailure(target=target, error=exc))
            continue

        removed.append(target)

    return CleanExecutionResult(
        removed=tuple(removed),
        failures=tuple(failures),
    )
