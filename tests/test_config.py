"""Tests for py-clean-tools configuration loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from py_clean_tools.cleaner import build_clean_plan
from py_clean_tools.config import load_config


def test_load_config_without_pyproject_uses_defaults(tmp_path: Path) -> None:
    """Missing pyproject.toml should use default exclusions."""
    config = load_config(tmp_path)

    assert ".git" in config.excluded_dirs
    assert ".pixi" in config.excluded_dirs
    assert "node_modules" in config.excluded_dirs


def test_load_config_without_tool_section_uses_defaults(tmp_path: Path) -> None:
    """Missing [tool.py-clean-tools] section should use default exclusions."""
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[project]
name = "sample"
version = "0.1.0"
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert ".git" in config.excluded_dirs
    assert ".pixi" in config.excluded_dirs


def test_load_config_reads_project_exclude_dirs(tmp_path: Path) -> None:
    """Project exclude_dirs should be merged with default exclusions."""
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-clean-tools]
exclude_dirs = ["sandbox", "litterature"]
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert "sandbox" in config.excluded_dirs
    assert "litterature" in config.excluded_dirs
    assert ".git" in config.excluded_dirs


def test_load_config_rejects_non_list_exclude_dirs(tmp_path: Path) -> None:
    """exclude_dirs must be a list."""
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-clean-tools]
exclude_dirs = "sandbox"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="exclude_dirs must be a list of strings"):
        _ = load_config(tmp_path)


def test_load_config_rejects_non_string_exclude_dir_item(tmp_path: Path) -> None:
    """exclude_dirs must contain only strings."""
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-clean-tools]
exclude_dirs = ["sandbox", 123]
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="exclude_dirs must contain only strings"):
        _ = load_config(tmp_path)


def test_build_clean_plan_ignores_configured_excluded_dirs(tmp_path: Path) -> None:
    """Configured excluded directories should be ignored by the clean plan."""
    cache = tmp_path / "sandbox" / "module" / "__pycache__"
    cache.mkdir(parents=True)

    plan = build_clean_plan(tmp_path, excluded_dirs=["sandbox"])

    assert plan.is_empty

def test_load_config_ignores_invalid_tool_value(tmp_path: Path) -> None:
    """Invalid tool value should fall back to default exclusions."""
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
tool = "invalid"
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert ".git" in config.excluded_dirs
    assert ".pixi" in config.excluded_dirs

def test_load_config_ignores_invalid_py_clean_tools_value(tmp_path: Path) -> None:
    """Invalid py-clean-tools value should fall back to default exclusions."""
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool]
py-clean-tools = "invalid"
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert ".git" in config.excluded_dirs
    assert ".pixi" in config.excluded_dirs
