"""Project configuration loading for py-clean-tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib
from typing import TypeAlias, cast

from py_clean_tools.cleaner import DEFAULT_EXCLUDED_DIRS

TomlValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | list["TomlValue"]
    | dict[str, "TomlValue"]
    | None
)


@dataclass(frozen=True, slots=True)
class PyCleanConfig:
    """Configuration for py-clean-tools."""

    excluded_dirs: frozenset[str] = field(default_factory=lambda: DEFAULT_EXCLUDED_DIRS)


def _get_table(data: dict[str, TomlValue], key: str) -> dict[str, TomlValue] | None:
    """Return a nested TOML table when present."""
    value = data.get(key)

    if isinstance(value, dict):
        return value

    return None


def _get_string_list(data: dict[str, TomlValue], key: str) -> list[str]:
    """Return a string list from a TOML table."""
    value = data.get(key)

    if value is None:
        return []

    if not isinstance(value, list):
        msg = f"{key} must be a list of strings."
        raise TypeError(msg)

    strings: list[str] = []

    for item in value:
        if not isinstance(item, str):
            msg = f"{key} must contain only strings."
            raise TypeError(msg)

        strings.append(item)

    return strings


def load_config(root: Path) -> PyCleanConfig:
    """Load py-clean-tools configuration from pyproject.toml.

    Missing configuration is allowed and falls back to safe defaults.
    """
    pyproject_path = root / "pyproject.toml"

    if not pyproject_path.is_file():
        return PyCleanConfig()

    with pyproject_path.open("rb") as file:
        raw_data = tomllib.load(file)

    data = cast(dict[str, TomlValue], raw_data)

    tool_data = _get_table(data, "tool")
    if tool_data is None:
        return PyCleanConfig()

    config_data = _get_table(tool_data, "py-clean-tools")
    if config_data is None:
        return PyCleanConfig()

    user_excluded_dirs = _get_string_list(config_data, "exclude_dirs")

    return PyCleanConfig(
        excluded_dirs=frozenset(DEFAULT_EXCLUDED_DIRS | frozenset(user_excluded_dirs))
    )
