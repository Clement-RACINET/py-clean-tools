from __future__ import annotations

from pathlib import Path

from py_clean_tools.cleaner import (
    build_clean_plan,
    execute_clean_plan,
    is_excluded,
    iter_dirs,
    remove_target,
)


def test_build_clean_plan_finds_python_cache_and_bytecode(tmp_path: Path) -> None:
    cache_dir = tmp_path / "pkg" / "__pycache__"
    cache_dir.mkdir(parents=True)
    pyc_file = cache_dir / "module.pyc"
    _ = pyc_file.write_text("", encoding="utf-8")

    plan = build_clean_plan(tmp_path)

    paths = {target.path for target in plan.targets}

    assert cache_dir in paths
    assert pyc_file in paths


def test_build_clean_plan_ignores_pixi_directory(tmp_path: Path) -> None:
    pixi_cache = tmp_path / ".pixi" / "envs" / "dev" / "__pycache__"
    pixi_cache.mkdir(parents=True)

    plan = build_clean_plan(tmp_path)

    assert not plan.targets


def test_build_clean_plan_finds_root_egg_info_directory(tmp_path: Path) -> None:
    egg_info = tmp_path / "example.egg-info"
    egg_info.mkdir()

    plan = build_clean_plan(tmp_path)

    assert [target.path for target in plan.targets] == [egg_info]


def test_build_clean_plan_finds_root_coverage_files(tmp_path: Path) -> None:
    coverage_file = tmp_path / "coverage.xml"
    dot_coverage_file = tmp_path / ".coverage"

    _ = coverage_file.write_text("<coverage />", encoding="utf-8")
    _ = dot_coverage_file.write_text("", encoding="utf-8")

    plan = build_clean_plan(tmp_path)

    assert {target.path for target in plan.targets} == {
        coverage_file,
        dot_coverage_file,
    }


def test_build_clean_plan_finds_build_artifacts(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    dist_dir = tmp_path / "dist"
    htmlcov_dir = tmp_path / "htmlcov"

    build_dir.mkdir()
    dist_dir.mkdir()
    htmlcov_dir.mkdir()

    plan = build_clean_plan(tmp_path)

    assert {target.path for target in plan.targets} == {
        build_dir,
        dist_dir,
        htmlcov_dir,
    }


def test_build_clean_plan_deduplicates_targets(tmp_path: Path) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()

    plan = build_clean_plan(
        tmp_path,
        dir_names=["__pycache__"],
        dir_globs=["__pycache__"],
    )

    assert [target.path for target in plan.targets] == [cache_dir]


def test_build_clean_plan_respects_custom_patterns(tmp_path: Path) -> None:
    custom_dir = tmp_path / ".custom_cache"
    custom_file = tmp_path / "artifact.tmp"

    custom_dir.mkdir()
    _ = custom_file.write_text("", encoding="utf-8")

    plan = build_clean_plan(
        tmp_path,
        dir_names=[".custom_cache"],
        file_globs=["*.tmp"],
    )

    assert {target.path for target in plan.targets} == {custom_dir, custom_file}


def test_is_excluded_returns_true_for_path_outside_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-file.txt"

    assert is_excluded(outside, tmp_path, excluded_dirs=[])


def test_is_excluded_returns_true_inside_excluded_directory(tmp_path: Path) -> None:
    path = tmp_path / ".venv" / "file.py"

    assert is_excluded(path, tmp_path, excluded_dirs=[".venv"])


def test_is_excluded_returns_false_for_allowed_path(tmp_path: Path) -> None:
    path = tmp_path / "pkg" / "file.py"

    assert not is_excluded(path, tmp_path, excluded_dirs=[".venv"])


def test_iter_dirs_returns_non_excluded_directories(tmp_path: Path) -> None:
    included = tmp_path / "pkg"
    excluded = tmp_path / ".pixi" / "envs"

    included.mkdir()
    excluded.mkdir(parents=True)

    assert list(iter_dirs(tmp_path, excluded_dirs=[".pixi"])) == [included]


def test_remove_target_removes_file(tmp_path: Path) -> None:
    file_path = tmp_path / "coverage.xml"
    _ = file_path.write_text("", encoding="utf-8")

    remove_target(
        build_clean_plan(
            tmp_path,
            file_globs=["coverage.xml"],
            dir_names=[],
            dir_globs=[],
        ).targets[0]
    )

    assert not file_path.exists()


def test_execute_clean_plan_removes_targets(tmp_path: Path) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()

    plan = build_clean_plan(tmp_path)
    removed = execute_clean_plan(plan)

    assert removed == 1
    assert not cache_dir.exists()


def test_execute_clean_plan_skips_missing_targets(tmp_path: Path) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()

    plan = build_clean_plan(tmp_path)
    cache_dir.rmdir()

    removed = execute_clean_plan(plan)

    assert removed == 0
