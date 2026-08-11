# py-clean-tools

Safe cleanup utility for Python project cache and build artifacts.

`py-clean-tools` provides a small command-line tool, `pyclean`, designed to remove common Python development artifacts from a repository.

It is conservative by default:

- dry-run by default;
- deletes files only when `--write` is passed;
- supports CI validation with `--check`;
- ignores virtual environments, Pixi environments, VCS directories, and Node dependencies;
- has no runtime dependency.

---

## Features

- Remove Python bytecode caches:
  - `__pycache__`
  - `*.pyc`
  - `*.pyo`
  - `*.pyd`
- Remove test and type-checking caches:
  - `.pytest_cache`
  - `.mypy_cache`
  - `.ruff_cache`
  - `.pyre`
  - `.pytype`
- Remove build artifacts:
  - `dist`
  - `build`
  - `*.egg-info`
- Remove coverage artifacts:
  - `.coverage`
  - `coverage.xml`
  - `htmlcov`
- Skip unsafe or external directories by default:
  - `.git`
  - `.hg`
  - `.svn`
  - `.pixi`
  - `.venv`
  - `venv`
  - `node_modules`
  - `__pypackages__`

---

## Installation

Install from PyPI once published:

```bash
pip install py-clean-tools
```

For local development with Pixi:

```bash
pixi install -e dev
```

---

## Usage

### Dry-run mode

By default, `pyclean` only prints what would be removed.

```bash
pyclean
```

Example:

```text
DRY-RUN — nothing will be deleted.

  [DRY-RUN] Would remove: pkg/__pycache__
  [DRY-RUN] Would remove: .pytest_cache

2 item(s) would be removed.
```

---

### Remove cleanup targets

Use `--write` to actually delete files and directories.

```bash
pyclean --write
```

---

### CI check mode

Use `--check` to fail when cleanup targets are found.

```bash
pyclean --check
```

This is useful in CI to ensure generated caches and build artifacts are not committed.

Exit codes:

| Code | Meaning                                                    |
| ---: | ---------------------------------------------------------- |
|  `0` | No cleanup target found, or cleanup completed successfully |
|  `1` | Cleanup targets found in `--check` mode                    |

---

### Clean another root

By default, `pyclean` uses the current working directory as the project root.

To clean another directory:

```bash
pyclean --root path/to/project --write
```

---

## Default targets

### Directories

The following directory names are removed recursively when found outside excluded directories:

```text
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
.pyre
.pytype
htmlcov
dist
build
```

The following root-level directory glob patterns are also supported:

```text
*.egg-info
```

---

### Files

The following files are removed recursively when found outside excluded directories:

```text
*.pyc
*.pyo
*.pyd
.coverage
coverage.xml
```

---

### Excluded directories

The following directories are ignored by default:

```text
.git
.hg
.svn
.pixi
.venv
venv
node_modules
__pypackages__
```

---

## Pixi integration

In a consuming project, add `py-clean-tools` to the development dependencies.

```toml
[feature.dev.pypi-dependencies]
py-clean-tools = ">=0.1.0,<0.2"
```

Then expose Pixi tasks:

```toml
[feature.dev.tasks]
clean-cache = "pyclean --write"
clean-check = "pyclean --check"
```

Example usage:

```bash
pixi run -e dev clean-cache
pixi run -e dev clean-check
```

---

## Development

Install the development environment:

```bash
pixi install -e dev
```

Run the checks:

```bash
pixi run fmt
pixi run lint
pixi run typecheck
pixi run tests
```

Run all checks if configured:

```bash
pixi run check
```

---

## Safety model

`pyclean` is intentionally safe by default.

Running:

```bash
pyclean
```

will never delete files.

Deletion only happens with:

```bash
pyclean --write
```

For CI, prefer:

```bash
pyclean --check
```

This makes accidental cleanup unlikely while keeping local and automated workflows simple.

---

## License

This project is distributed under the MIT License with an additional
no-endorsement clause.

See [`LICENSE`](LICENSE) for details.
