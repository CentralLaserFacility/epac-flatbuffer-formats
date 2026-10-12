# EPAC Flatbuffer Formats
Version: {sub-ref}`version`

[![Latest release](https://img.shields.io/github/v/release/CentralLaserFacility/epac-flatbuffer-formats?color=blue)](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/releases/latest)

This repository contains the canonical schema definitions for the flatbuffer
data formats used in the [EPAC][epac] data management system.

It comprises:

1. Flatbuffers schema definitions
2. A Python library for serialisation and deserialisation of all schemas
3. A set of Rust crates providing support for serialising the `pva0` schema

## Available Schema

`pva0` is the favoured singular schema and the only schema for which Rust serialisation is supported.

The `f142` and `ADAr` schemas are heavily based on/copied from the
[ESS schemas][streaming-data-types] and [ESS code][python-streaming-data-types].
Code using the ESS `streaming_data_types` package should be able to be ported to
this package with few if any changes beyond the import path.

| Schema         | Description                                         |
| -------------- | --------------------------------------------------- |
| [`pva0`](pva0) | EPICS PVAccess Data                                 |
| [`f142`](f142) | ***Deprecated*** - Log Data                         |
| [`ADAr`](adar) | ***Deprecated*** - EPICS areaDetector data          |
| [`wa00`](wa00) | ***Deprecated*** - EPICS Waveform data              |

See the [Schema Details](schema-details) section for more information.

[streaming-data-types]: https://github.com/ess-dmsc/streaming-data-types
[python-streaming-data-types]: https://github.com/ess-dmsc/python-streaming-data-types
[epac]: https://clf.stfc.ac.uk/facility/epac/

## Table of Contents

::::{grid} 2
:gutter: 3

:::{grid-item-card}
```{toctree}
:titlesonly:
:maxdepth: 3

_content/get_started/index
```
+++
Tutorials for getting started.
:::

:::{grid-item-card}
```{toctree}
:titlesonly:
:maxdepth: 3

_content/user_guide/index
```
+++
Practical guides for common use cases.
:::

:::{grid-item-card}
```{toctree}
:titlesonly:
:maxdepth: 3

_content/explanations/index
```
+++
Higher level discussion and explanations.
:::

:::{grid-item-card}
```{toctree}
:titlesonly:
:maxdepth: 2

_content/reference/index
```
+++
Technical reference.
:::

::::
