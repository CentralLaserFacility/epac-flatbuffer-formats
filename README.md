# EPAC Flatbuffer Formats

[![Latest release](https://img.shields.io/github/v/release/CentralLaserFacility/epac-flatbuffer-formats?color=blue)](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/releases/latest)
[![License](https://img.shields.io/badge/License-BSD_2--Clause-orange.svg)](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/blob/development/COPYRIGHT)
[![CI](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/actions/workflows/code.yml/badge.svg)](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/actions/workflows/code.yml)

This repository provides the canonical FlatBuffers schemas and Python
serialisation support used by the EPAC data management system. Optional Rust
bindings provide an additional `pva0` serializer.

`pva0` is the recommended schema for new PVAccess integrations. The `f142`,
`ADAr`, and `wa00` schemas are deprecated but remain available for compatibility.

| Source | https://github.com/CentralLaserFacility/epac-flatbuffer-formats |
| :--- | :--- |
| Documentation | https://centrallaserfacility.github.io/epac-flatbuffer-formats/ |
| Releases | https://github.com/CentralLaserFacility/epac-flatbuffer-formats/releases/ |

The Python package is not published on PyPI. See the
[installation guide](docs/source/_content/get_started/installation.md) for
release and development installation options.

## Repository contents

- [`schemas/`](schemas/) — canonical FlatBuffers schema definitions.
- [`src/`](src/) — Python serializers, deserializers, and data models.
- [`rust/`](rust/) — Rust crates and optional Python bindings for `pva0`.
