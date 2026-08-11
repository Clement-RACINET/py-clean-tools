from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from py_clean_tools.cli import CliArgs, entrypoint, main, parse_args

if TYPE_CHECKING:
    import pytest


def test_parse_args_uses_current_directory_by_default() -> None:
    args = parse_args([])

    assert isinstance(args, CliArgs)
    assert args.root == Path.cwd()
    assert not args.write
    assert not args.check


def test_parse_args_reads_flags(tmp_path: Path) -> None:
    args = parse_args(["--root", str(tmp_path), "--write", "--check"])

    assert args.root == tmp_path
    assert args.write
    assert args.check


def test_cli_dry_run_does_not_remove_target(tmp_path: Path) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()

    exit_code = main(["--root", str(tmp_path)])

    assert exit_code == 0
    assert cache_dir.exists()


def test_cli_dry_run_reports_nothing_to_clean(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["--root", str(tmp_path)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Nothing to clean." in captured.out


def test_cli_write_removes_target(tmp_path: Path) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()

    exit_code = main(["--root", str(tmp_path), "--write"])

    assert exit_code == 0
    assert not cache_dir.exists()


def test_cli_write_reports_removed_target(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()

    exit_code = main(["--root", str(tmp_path), "--write"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "[REMOVED]" in captured.out
    assert "1 item(s) removed." in captured.out


def test_cli_check_fails_when_targets_exist(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()

    exit_code = main(["--root", str(tmp_path), "--check"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Cleanup targets found:" in captured.out
    assert "[FOUND]" in captured.out


def test_cli_check_passes_when_no_targets_exist(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["--root", str(tmp_path), "--check"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "No cleanup targets found." in captured.out


def test_entrypoint_raises_system_exit_for_empty_root(tmp_path: Path) -> None:
    try:
        entrypoint(["--root", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code == 0
