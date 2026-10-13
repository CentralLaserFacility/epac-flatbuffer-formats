(installation)=
# Installation

The Python package is not published on PyPI. It can be installed from a GitHub release
or directly from the repository.

This package includes pure-Python serializers/deserializers for the schema. Optional Rust bindings add a second implementation for the `pva0` serializer.

In general, you should:
- Add the package as a dependency when it is required by your project.
- Use the published wheel for normal installations.
- Install directly from Git when you need a specific tagged release without cloning the repository.
- Perform a development installation when contributing to the project or testing local modifications.

## Prerequisites

- Python 3.10 or newer
- Git (if installing from the repository)

Building the optional Rust bindings from source also requires the Rust toolchain.

```{note}
The Rust-binding package is optional, the pure-Python package can serialise and deserialise `pva0` data without it.
```

## Install from a release

Download the Python wheel(s) from the
[GitHub releases](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/releases)
page. The release includes:

- the main Python package wheel, such as `epac_flatbuffer_formats-0.3.2-py3-none-any.whl`
- the optional Rust-binding Python package wheel, such as `epac_flatbuffer_formats_rs-0.3.2-cp38-abi3-manylinux_2_34_x86_64.whl`

Install the main package with:

```shell
python -m pip install /path/to/downloaded-python-wheel.whl
```

To use the Rust `pva0` serializer as well, install the matching Rust-binding package in the same environment:

```shell
python -m pip install /path/to/downloaded-python-wheel.whl \
    /path/to/downloaded-rust-wheel.whl
```

Replace both paths with the downloaded filenames.

## Install from Git

To install the pure-Python package directly from a tagged release, run:

```shell
python -m pip install \
    "epac-flatbuffer-formats @ git+https://github.com/CentralLaserFacility/epac-flatbuffer-formats.git@v0.3.2"
```

To install both the Python package and the Rust-binding Python package together from the same tag, run:

```shell
python -m pip install \
    "epac-flatbuffer-formats @ git+https://github.com/CentralLaserFacility/epac-flatbuffer-formats.git@v0.3.2" \
    "epac-flatbuffer-formats-rs @ git+https://github.com/CentralLaserFacility/epac-flatbuffer-formats.git@v0.3.2"
```

Replace `v0.3.2` with the release tag you want to use. The Rust package is optional, but if you want to use the Rust `pva0` serializer you should install it alongside the main package.


## Install for development

Clone the repository and set up the development environment:

```shell
git clone https://github.com/CentralLaserFacility/epac-flatbuffer-formats.git
cd epac-flatbuffer-formats
./dev.py setup venv
```

This creates `.venv` and installs the project in editable mode with its
development dependencies. Activate it with:

```shell
source .venv/bin/activate
```

To build and install the optional Rust bindings in this environment, install
the Rust toolchain and run:

```shell
./dev.py setup rust-bindings
./dev.py rust-develop
```

```{warning}
The `rust-develop` build does not use release mode.
```

## Install as dependencies

If your project uses `pyproject.toml` to manage its virtual environment (as is common in the EPAC data umbrella), add the packages to your `pyproject.toml` dependencies.

```toml
[project]
...
dependencies = [
    "epac-flatbuffer-formats @ git+https://github.com/CentralLaserFacility/epac-flatbuffer-formats.git@v0.3.2",
    "epac-flatbuffer-formats-rs @ git+https://github.com/CentralLaserFacility/epac-flatbuffer-formats.git@v0.3.2",
]
```

Replace `v0.3.2` with the release tag you want to use. Then refresh the environment so the dependencies are installed.

If you do not need the Rust-backed serializer, you can omit `epac-flatbuffer-formats-rs` and install only the main package.

## Verify the installation

Check that Python can import the package:

```shell
python -c "from epac.flatbuffers.pva0_data import serialise_data; print('Installation OK')"
```

The command should print:

```text
Installation OK
```

Similarly, to check that python can import the Rust bindings:

```shell
python -c "from epac_flatbuffer_formats_rs import serialise_pv_data; print('Installation OK')"
```

The command should print:

```text
Installation OK
```