# Project Structure

TODO Update with rust structure

The repository is organised into six top-level directories:

- `src/` – Application source code
- `tests/` – Test code
- `benchmarks/` - Benchmarking code
- `rust/` - Rust source code
- `schemas/` - Flatbuffer schema definitions
- `docs/` – Documentation source and build artefacts
- `.github/` – GitHub Actions workflows and repository automation

All Python source code should reside within `src/`. Corresponding tests should be placed in `tests/`, where they are automatically executed as part of the CI pipeline.
Rust code should reside within `rust/`. Details of the rust crate structure can be found in [Overview of Rust Crates](rust-crates).

There are also five files present in the root directory:

- `pyproject.toml` - Package configuration
- `dev.py` - Developer tooling
- `.gitignore` - Version control configuration
- `README.md` - Repository Overview
- `COPYRIGHT` - Copyright details

## Documentation Structure

The `docs/` directory contains the source files and generated output for the project's documentation.

### Directory Layout

- `source/` – Documentation source files used by Sphinx
- `build/` – Generated documentation output (not intended for manual editing)

### Sphinx Configuration

The `conf.py` file contains the Sphinx configuration for the documentation build.

### Documentation Content

Documentation pages are organised under `source/` into the following sections:

- `content/get_started/` – Getting started guides and onboarding material
- `content/user_guide/` – User-facing guides and tutorials
- `content/explanations/` – Background concepts and explanatory content
- `content/reference/` – Reference documentation

New documentation pages should be added to the appropriate content directory.

Generated API documentation is written to:

- `content/reference/api_docs/`

### Static Assets and Templates

Additional documentation resources are stored in:

- `_static/` – Static assets such as images and other media
- `_templates/` – Custom Sphinx templates

The Rust API documentation is added to `static/` as html files when the documentation is built.

The documentation landing page is defined in:

- `source/index.md`