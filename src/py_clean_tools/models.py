"""Data models for cleanup planning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CleanTarget:
    """A filesystem target selected for cleanup."""

    path: Path
    reason: str


@dataclass(frozen=True, slots=True)
class CleanPlan:
    """A cleanup plan containing all selected targets."""

    targets: tuple[CleanTarget, ...]

    @property
    def is_empty(self) -> bool:
        """Return whether the plan contains no cleanup target."""
        return not self.targets
