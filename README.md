# EPAC flatbuffer formats

This repository contains the canonical schema definitions for the flatbuffer
data formats used in the EPAC data management system, as well as Python code to
serialise and deserialise those formats.

Both of these are heavily based on/copied from the
[ESS schemas][streaming-data-types] and [ESS code][python-streaming-data-types].
Code using the ESS `streaming_data_types` package should be able to be ported to
this package with few if any changes beyond the import path.

## Getting started

The package can be installed through `pip` as usual, although it is not
(currently) available on PyPI.  Clone this repository, set up a virtual
environment, and run `pip install .`.

To add this repository as a dependency to another project, you need to use pip's
support for git URLs. For example, you can add the following to your
`pyproject.toml`:

```toml
dependencies = [
    "epac-flatbuffer-formats @ git+https://github.com/CentralLaserFacility/epac-flatbuffer-formats@v0.1.0",
]
```

Each data format can be serialised and deserialised in a similar way. For
example, for `f142` (for recording values from a single PV):

```python
import time

from epac.flatbuffers.logdata_f142 import (
    deserialise_f142,
    serialise_f142,
    AlarmStatus,
    AlarmSeverity,
)

encoded_value = serialise_f142(42,
    source_name="MY:PV:NAME",
    timestamp_unix_ns=time.time() * 1e9,
    alarm_status=AlarmStatus.NO_ALARM,
    alarm_severity=AlarmSeverity.NO_ALARM,
)

...

decoded_value = deserialise_f142(buf)
print(decoded_value.value)
```

## Comparison with upstream

The "upstreams" for this project are two ESS projects:
[`streaming-data-types`][streaming-data-types] and
[`python-streaming-data-types`][python-streaming-data-types]. Specific schemas
that will or might be used in EPAC have been copied into this repository, to
which EPAC-specific schemas have been added. This repository then serves as a
canonical location for all the schemas used in EPAC.

Unlike upstream, the Python support code is stored in the same repository, which
helps keep our generated code in sync with the schema definitions. The Python
code taken from upstream has been modified as necessary to pass our CI steps.

Where there is overlap, we aim to maintain compatibility with upstream, so that
any code using the Python [`streaming_data_types`][python-streaming-data-types]
package (`ess-streaming-data-types` on PyPI) can be adapted to use this package
with little effort beyond changing the import paths.

### Major differences with upstream

Most schemas present in upstream are missing. At the time of writing, only
`f142` and `ADAr` have been kept.

At the time of writing,
[`python-streaming-data-types`][python-streaming-data-types] allows strings and
string arrays to be serialied to `f142`. As the string variants have been
removed from the [`streaming-data-types`][streaming-data-types] version of the
`f142` schema, we have also removed support for string serialisation.

## Development

There are four main bodies of code. Each schema should have:

- A definition in `schemas/`. The name should start with the file identifier
- Generated code in `src/epac/flatbuffers/fbschemas`. The subfolder containing
  the generated code should have the same name as the schema file
- Higher-level bindings under `src/epac/flatbuffers`. The name of the module
  should contain the file identifier, but is otherwise flexible. User code
  should not need to import anything from the generated code - useful enum
  definitions should be re-exported.
- Tests in `tests/test_<file_id>.py`

Code generated by a specific version of the Flatbuffers compiler `flatc` is
committed to the repository as a convenience. You won't need to worry about this
unless you're adding or modifying schemas or need to change how code is
generated. However, code under `src/epac/flatbuffers/fbschemas` must not be
modified by hand. See below for more details on
[how generated code is handled](#generated-code).

### Setup

Common development tasks can be automated using the included `dev.py` script.
To set up a virtual environment for development (in `.venv/`), run:

```shell
$ ./dev.py setup venv
```

Once that has been done, you can use `./dev.py run` to run any command in that
virtual environment. A number of other commands are supported: see `./dev.py
--help`.

To set up a Git pre-commit hook, run:

```shell
$ ./dev.py setup hooks
```

This should prevent you from making commits that fail linting. You can run the
pre-commit checks without making a commit by running:

```shell
$ ./dev.py pre-commit
```

But note that the real pre-commit hook will check the exact code that will be
committed by first stashing any unstaged changes or untracked files, so you
may not get exactly the same results.

### Generated code

Generated code must be generated by a specific version of `flatc`, then a number
of custom post-processing steps are needed. This is all handled by
`./dev.py schema-generate`. This in turn requires the correct version of `flatc`
to be installed with `./dev.py setup flatc`, which in turn requires the venv to
be set up.

Therefore, to regenerate schema definitions from a freshly checked-out
repository, you will need to run the following steps:

```shell
$ ./dev.py setup venv
$ ./dev.py setup flatc
$ ./dev.py schema-generate
```

A dedicated CI job checks that the generated code committed to the repository
matches what would be generated by a fresh invocation of
`./dev.py schema-generate`. You should only need to regenerate the code (and
hence install `flatc`) if you are modifying the schema definitions or the
generation process.

[streaming-data-types]: https://github.com/ess-dmsc/streaming-data-types
[python-streaming-data-types]: https://github.com/ess-dmsc/python-streaming-data-types
